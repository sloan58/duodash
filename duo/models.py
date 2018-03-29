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
    users = models.ManyToManyField(User)


# Duo Token model
class Token(models.Model):
    serial = models.CharField(max_length=200, unique=True)
    token_id = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    totp_step = models.CharField(max_length=200, null=True)
    users = models.ManyToManyField(User)


# Duo Phone model
class Phone(models.Model):
    phone_id = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200, null=True)
    number = models.CharField(max_length=200, null=True)
    extension = models.CharField(max_length=200, null=True)
    type = models.CharField(max_length=200, null=True)
    platform = models.CharField(max_length=200, null=True)
    postdelay = models.CharField(max_length=200, null=True)
    predelay = models.CharField(max_length=200, null=True)
    sms_passcodes_sent = models.CharField(max_length=200, null=True)
    activated = models.CharField(max_length=200, null=True)
    users = models.ManyToManyField(User)

