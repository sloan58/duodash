from django.db import models


# Duo User model
class User(models.Model):
    user_id = models.CharField(max_length=200, unique=True)
    username = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    realname = models.CharField(max_length=200, null=True)
    notes = models.CharField(max_length=200)
    last_login = models.DateTimeField('last login', null=True)
