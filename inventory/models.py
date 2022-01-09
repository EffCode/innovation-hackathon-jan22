from django.db import models

from user.models import User


class Category(models.Model):
    category = models.CharField(max_length=50)
    category_mr = models.CharField(max_length=50, null=True)
    category_hi = models.CharField(max_length=50, null=True)


class Inventory(models.Model):
    item_code = models.CharField(max_length=10)
    name = models.CharField(max_length=200)
    name_mr = models.CharField(max_length=200, null=True)
    name_hi = models.CharField(max_length=200, null=True)
    brand = models.CharField(max_length=100)
    brand_mr = models.CharField(max_length=100, null=True)
    brand_hi = models.CharField(max_length=100, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.TextField(null=True)
    description_mr = models.TextField(null=True)
    description_hi = models.TextField(null=True)
    color = models.CharField(max_length=20, null=True)
    color_mr = models.CharField(max_length=20, null=True)
    color_hi = models.CharField(max_length=20, null=True)
    size = models.CharField(max_length=10, null=True)
    qty = models.IntegerField(default=0)
    price = models.CharField(max_length=10)
    image = models.URLField(null=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    qty = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(null=True)


class Order(models.Model):
    order_id = models.CharField(max_length=10)
    rz_py_resp = models.JSONField()
    order_products = models.JSONField()
    payment_status = models.CharField(max_length=10, default='pending')
    rz_invoice_id = models.CharField(max_length=20, null=True)
    rz_payment_id = models.CharField(max_length=30, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(null=True)
