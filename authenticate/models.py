from django.db import models
from django.db.models import CharField, OneToOneField,CASCADE
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .manager import CustomUserManager
# Create your models here.
class Our_Users(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.IntegerField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    
    objects = CustomUserManager()   # 🔥 THIS IS MANDATORY


    def __str__(self):
        return self.email
    
class Identity(models.Model):
    session_key=CharField(max_length=100,null=True,blank=True)
    our_users=OneToOneField(Our_Users,on_delete=CASCADE,related_name='identity',blank=True,null=True)
    
    def is_authenticated(self):
        return self.our_users is not None
    
