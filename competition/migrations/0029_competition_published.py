# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-02-05 05:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0028_auto_20180201_2349'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='published',
            field=models.BooleanField(default=False, verbose_name='Published'),
        ),
    ]