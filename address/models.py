from django.db import models
from django.db.models import CharField, ForeignKey, PositiveIntegerField, BooleanField, CASCADE

from authenticate.models import Identity
# Create your models here.

class Address (models.Model):
    identity = ForeignKey(Identity, on_delete=CASCADE, null=True, blank=True)
    
    name = CharField(max_length=100)
    phone_number = CharField(max_length=15)
    pincode = CharField(max_length=6)
    state = CharField(max_length=20)
    city = CharField(max_length=20)
    house_no_or_street =CharField(max_length=500)
    landmark = CharField(max_length=500, blank=True, null=True)
    is_default = BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name - self.city}"
