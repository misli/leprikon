# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-08-28 09:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leprikon', '0027_journals'),
    ]

    operations = [
        migrations.AddField(
            model_name='agegroup',
            name='require_school',
            field=models.BooleanField(default=True, verbose_name='require school'),
        ),
    ]