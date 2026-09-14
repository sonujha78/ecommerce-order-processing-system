from django.db import models


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_qty = models.IntegerField()

    class Meta:
        managed = False
        db_table = "products"


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    customer_id = models.IntegerField()
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "orders"


class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField()
    product_id = models.IntegerField()
    quantity = models.IntegerField()

    class Meta:
        managed = False
        db_table = "order_items"


class OrderEvent(models.Model):
    event_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField()
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "order_events"
