# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-29 07:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Marcus', '0002_remotecamera_ip_addr'),
    ]

    operations = [
        migrations.AddField(
            model_name='remotecamera',
            name='uuid',
            field=models.CharField(default='9b021d82-f5b7-4b68-b955-05166cd88cfb', max_length=36),
            preserve_default=False,
        ),
    ]
