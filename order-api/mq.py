import pika
import os
import json
from dotenv import load_dotenv

load_dotenv()

def get_rabbitmq_connection():
    credentials = pika.PlainCredentials(
        os.getenv("RABBITMQ_USER"),
        os.getenv("RABBITMQ_PASSWORD")
    )
    return pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST"),
            port=int(os.getenv("RABBITMQ_PORT")),
            credentials=credentials
        )
    )

def publish_order_created(order_payload: dict):
    connection = get_rabbitmq_connection()
    channel = connection.channel()

    channel.exchange_declare(exchange="orders_exchange", exchange_type="direct", durable=True)
    channel.queue_declare(queue="order.created", durable=True)
    channel.queue_bind(queue="order.created", exchange="orders_exchange", routing_key="order.created")

    channel.basic_publish(
        exchange="orders_exchange",
        routing_key="order.created",
        body=json.dumps(order_payload),
        properties=pika.BasicProperties(delivery_mode=2)  # persistent message
    )
    connection.close()
