from django.db import models
from django.db.models import CharField, OneToOneField, CASCADE, IntegerField, DateTimeField

from authenticate.models import Identity, Our_Users
# Create your models here.

class Userprofile(models.Model):
    our_users = OneToOneField(Our_Users,on_delete=CASCADE,null=True,blank=True,related_name="profile")
    
    first_name = CharField('First Name',max_length=150,null=True)
    last_name = CharField('Last Name',max_length=150,null=True)
    phone_num = CharField('Phn. No.:',null=True,max_length=13)
    gender=CharField('Gender',max_length=50,null=True)
    
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.first_name
    
    