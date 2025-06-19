# mainApp/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    pin = models.CharField(max_length=10, help_text="Gym PIN for API access")
    goal = models.IntegerField(default=0, help_text="Weekly gym visit goal")
    notificationEmail = models.EmailField(blank=True, null=True, help_text="Email for notifications")

    # Use email as the unique identifier for login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class UserList(models.Model):
    username = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    pin = models.CharField(max_length=200)
    notificationEmail = models.CharField(max_length=200)
    goal = models.IntegerField()