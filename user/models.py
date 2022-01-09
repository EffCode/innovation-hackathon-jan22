from django.db import models

# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=13)
    token = models.CharField(max_length=200, null=True)
    address = models.TextField(null=True)
    lang = models.CharField(default="en", max_length=10)
