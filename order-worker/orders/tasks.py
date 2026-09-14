import logging
from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction
from django.conf import settings
from kombu import Connection, Exchange, Queue

from .models import Order, OrderItem, Product, OrderEvent

logger = get_task_logger(__name__)

DLQ_QUEUE_NAME = "order_processing_dlq"


def send_to_dlq(payload, reason):
    with Connection(settings.CELERY_BROKER_URL) as conn:
        dlq_exchange = Exchange("dlq_exchange", type="direct", durable=True)
        dlq_queue = Queue(DLQ_QUEUE_NAME, exchange=dlq_exchange,
                           routing_key=DLQ_QUEUE_NAME, durable=True)
        producer = conn.Producer()
        producer.publish(
            {"payload": payload, "reason": reason},
            exchange=dlq_exchange,
            routing_key=DLQ_QUEUE_NAME,
            declare=[dlq_queue],
            retry=True,
        )
    logger.error(f"Order {payload.get('order_id')} sent to DLQ: {reason}")


def mark_failed_and_dlq(order_id, payload, reason):
    if order_id and Order.objects.filter(order_id=order_id).exists():
        Order.objects.filter(order_id=order_id).update(status="failed")
        OrderEvent.objects.create(order_id=order_id, event_type="order.failed", payload={"error": reason})
    else:
        logger.warning(f"Order {order_id} not found in DB — skipping status/event update, sending straight to DLQ.")
    send_to_dlq(payload, reason)


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def process_order(self, payload):
    order_id = payload.get("order_id")

    try:
        order = Order.objects.get(order_id=order_id)

        if order.status in ("confirmed", "failed"):
            logger.info(f"Order {order_id} already in terminal state '{order.status}' — skipping (idempotent).")
            return f"Order {order_id} already handled"

        items = list(OrderItem.objects.filter(order_id=order_id))

        with transaction.atomic():
            Order.objects.filter(order_id=order_id).update(status="processing")
            OrderEvent.objects.create(order_id=order_id, event_type="order.processing", payload=payload)

            for item in items:
                product = Product.objects.select_for_update().get(product_id=item.product_id)
                if product.stock_qty < item.quantity:
                    raise ValueError(f"Insufficient stock for product {item.product_id}")
                product.stock_qty -= item.quantity
                product.save()

            Order.objects.filter(order_id=order_id).update(status="confirmed")
            OrderEvent.objects.create(order_id=order_id, event_type="order.confirmed", payload=payload)

        logger.info(f"Order {order_id} confirmed.")
        return f"Order {order_id} confirmed"

    except ValueError as e:
        Order.objects.filter(order_id=order_id).update(status="failed")
        OrderEvent.objects.create(order_id=order_id, event_type="order.failed", payload={"error": str(e)})
        logger.warning(f"Order {order_id} failed: {e}")
        return f"Order {order_id} failed: {e}"

    except Exception as e:
        logger.error(f"Error processing order {order_id} (attempt {self.request.retries + 1}/{self.max_retries + 1}): {e}")

        if self.request.retries >= self.max_retries:
            mark_failed_and_dlq(order_id, payload, str(e))
            return f"Order {order_id} moved to DLQ after max retries"

        raise self.retry(exc=e)
