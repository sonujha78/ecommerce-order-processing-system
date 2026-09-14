import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")

BROKER_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}//"

celery_client = Celery("order_api_client", broker=BROKER_URL)


def publish_order_created(order_payload: dict):
    celery_client.send_task(
        "orders.tasks.process_order",
        args=[order_payload],
        queue="order_processing"
    )
