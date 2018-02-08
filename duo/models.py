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


# Duo Group model
class Group(models.Model):
    group_id = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200)
    desc = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    mobile_otp_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=False)
    sms_enabled = models.BooleanField(default=False)
    voice_enabled = models.BooleanField(default=False)
