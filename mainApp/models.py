from django.db import models

class UserList(models.Model):
    username = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    pin = models.CharField(max_length=200)
    notificationEmail = models.CharField(max_length=200)
    goal = models.IntegerField()