# Generated by Django 2.0.2 on 2018-02-07 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('duo', '0003_auto_20180207_1609'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='realname',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
