# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-29 06:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Marcus', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='remotecamera',
            name='ip_addr',
            field=models.CharField(default=None, max_length=55),
            preserve_default=False,
        ),
    ]
