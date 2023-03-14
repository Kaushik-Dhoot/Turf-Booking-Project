from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from .manager import *
# from django import forms
# from django.conf import settings

# Create your models here.

class User(AbstractUser):
    email = None
    username = None
    phone = models.CharField(max_length=10,unique=True)
    phone_verified = models.BooleanField(default=False)
    booking_count = models.IntegerField(default=0)

    objects = UserManager()
    REQUIRED_FIELDS = []

    USERNAME_FIELD = 'phone'

class Slot_booking(models.Model):
    phone = models.CharField(max_length=10)
    # first_name = models.ForeignKey(User.first_name,related_name='booking_first_name', on_delete=models.CASCADE)
    # last_name = models.ForeignKey(User.last_name,related_name='booking_last_name', on_delete=models.CASCADE)
    # phone = models.ForeignKey('account.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total = models.IntegerField()
    # offer = models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return f'from {self.start_time} to {self.end_time}'

class Ratings(models.Model):
    name = models.TextField(max_length=20)
    comment = models.TextField(max_length=250,default=None)
    rate = models.IntegerField(default=0)
    created_at = models.DateField()

    def __str__(self):
        return f'{self.name}\'s Review'
    

    