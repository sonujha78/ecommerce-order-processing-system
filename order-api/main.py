from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import json
from db import get_connection
from mq import publish_order_created

app = FastAPI(title="Order API")


class OrderItem(BaseModel):
    product_id: int
    quantity: int


class OrderRequest(BaseModel):
    customer_id: int
    items: List[OrderItem]


@app.post("/orders", status_code=202)
def create_order(order: OrderRequest):
    if not order.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO orders (customer_id, status) VALUES (%s, %s)",
                (order.customer_id, "received")
            )
            order_id = cursor.lastrowid

            for item in order.items:
                cursor.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
                    (order_id, item.product_id, item.quantity)
                )

            payload = {
                "order_id": order_id,
                "customer_id": order.customer_id,
                "items": [item.dict() for item in order.items]
            }

            cursor.execute(
                "INSERT INTO order_events (order_id, event_type, payload) VALUES (%s, %s, %s)",
                (order_id, "order.created", json.dumps(payload))
            )

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

    # Publish to RabbitMQ AFTER commit succeeds — don't wait for processing
    publish_order_created(payload)

    return {"order_id": order_id, "status": "received"}


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM orders WHERE order_id=%s", (order_id,))
            order = cursor.fetchone()
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")

            cursor.execute("SELECT * FROM order_items WHERE order_id=%s", (order_id,))
            items = cursor.fetchall()

            cursor.execute("SELECT * FROM order_events WHERE order_id=%s ORDER BY created_at", (order_id,))
            events = cursor.fetchall()

        return {"order": order, "items": items, "events": events}
    finally:
        conn.close()


@app.get("/health")
def health():
    return {"status": "ok"}
