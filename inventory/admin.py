from django.contrib import admin

# Register your models here.
from inventory.models import Inventory, Category, Cart, CartProduct, Order

admin.site.register(Inventory)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(Order)
