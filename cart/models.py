from django.db import models
from django.db.models import ForeignKey, PositiveIntegerField, BooleanField, DateTimeField, CharField

from products.models import Products
from authenticate.models import Identity
# Create your models here.

class Cart(models.Model):
    identity = ForeignKey(Identity, on_delete=models.CASCADE, related_name="cart_items", null=True, blank=True)

    product = ForeignKey(Products, on_delete=models.CASCADE)
    quantity = PositiveIntegerField(default=1,null=True,blank=True)
    Save_For_Later = BooleanField(default=False,null=True,blank=True)
    timestamp = DateTimeField(auto_now_add=True,null=True,blank=True)  

    def __str__(self):
        return f"{self.identity.our_users} -- {self.product} -- {self.quantity}"
    
    @property
    def sub_total(self):
        return self.product.discounted_price * self.quantity
    