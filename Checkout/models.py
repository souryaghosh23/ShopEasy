from django.db import models
from django.db.models import ForeignKey, CharField, PositiveIntegerField, DecimalField,DateTimeField, ImageField, CASCADE, SET_NULL, ManyToManyField
from decimal import Decimal
from sequences import Sequence

from products.models import Products
from authenticate.models import Our_Users, Identity
from address.models import Address
# Create your models here.
  
class Checkout(models.Model):
    identity = ForeignKey(Identity, on_delete=CASCADE, null=True, blank=True)
    
    invoice = CharField(max_length=1000,null=False,unique=True,blank=False)
    full_name = CharField(max_length=100)
    address = ForeignKey(Address, on_delete=SET_NULL, null=True, blank=True)
    total_amount = DecimalField(decimal_places=2, max_digits=10)
    payment_method = CharField(max_length=50,null=False,blank=False)
    
    payment_status = CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Completed', 'Completed')],
        default='Pending'
    )
    order_status = CharField(
        max_length=20,
        choices=[('Placed', 'Placed'), ('Processing', 'Processing'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'),('Cancelled','Cancelled'),('Partially Cancelled','Partially Cancelled'),('Returned','Returned')],
        default='Not Placed'
    )
    created_at = DateTimeField(auto_now_add=True)
    @property
    def order_id(self):
        return f"#OD{self.invoice}"
    
class CheckoutItems(models.Model):
    identity = ForeignKey(Identity, on_delete=SET_NULL, null=True, blank=True)

    checkout = ForeignKey(Checkout,on_delete=CASCADE,null=True,related_name='items')
    product = ForeignKey(Products, on_delete=SET_NULL, null=True, blank=True)
    quantity = PositiveIntegerField()
    subtotal = DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    
    order_status = CharField(
        max_length=20,
        choices=[('Placed', 'Placed'), ('Processing', 'Processing'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'),('Cancelled','Cancelled'),('Returned','Returned')],
        default='Not Placed'
    )
    created_At = DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Checkoutitems #{self.id}"
  

class OrderItems(models.Model): #Snapshot model
    identity = ForeignKey(Identity, on_delete=CASCADE, null=True, blank=True)
    
    order = ForeignKey(CheckoutItems, on_delete=CASCADE, related_name='items', null=True, blank=True) 
    product_id = ForeignKey(Products, on_delete=SET_NULL, null=True, blank=True)
    product_name = CharField(max_length=500)
    product_price = DecimalField(max_digits=10, decimal_places=2)
    product_image = ImageField(upload_to="order_items/", null=True, blank=True)
    quantity = PositiveIntegerField()
    selected = models.BooleanField(default=True)
    sub_total = DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        self.sub_total = self.product_price * self.quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product_name} -- {self.quantity}"

    

    

