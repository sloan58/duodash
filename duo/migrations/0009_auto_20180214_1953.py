# Generated by Django 2.0.2 on 2018-02-14 19:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('duo', '0008_auto_20180214_1946'),
    ]

    operations = [
        migrations.RenameField(
            model_name='token',
            old_name='user',
            new_name='users',
        ),
    ]
