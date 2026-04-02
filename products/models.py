from django.db import models
from django.db.models import CharField, PositiveIntegerField, BooleanField, TextField, DecimalField, ImageField, ForeignKey
from django.db.models import CASCADE,DO_NOTHING
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.name:
            self.name=self.name.strip().lower()
        return super().save(*args, **kwargs)
    

class Products(models.Model):
    name = CharField(max_length=500, null=False, blank=False)
    original_price = DecimalField(max_digits=10,decimal_places=2,null=True, blank=True)
    discounted_price = DecimalField(max_digits=10,decimal_places=2, null=True, blank=True)
    description = TextField()
    inventory = PositiveIntegerField()
    image = ImageField(upload_to='products/', null= True, blank=True)
    pincode = CharField(max_length=10)
    reviews = DecimalField(decimal_places=1, max_digits=3, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    category=models.ForeignKey(Category,on_delete=DO_NOTHING,blank=False,null=False)
    # seller = ForeignKey(SellersIdentity,on_delete=CASCADE,related_name='product')
    
    def __str__(self):
        return self.name
    
# models.py

    
    
    

    