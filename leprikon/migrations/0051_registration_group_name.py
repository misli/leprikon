# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-03-26 20:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leprikon', '0050_orderables'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subjectregistrationgroup',
            name='name',
            field=models.CharField(blank=True, default='', max_length=150, verbose_name='group name'),
        ),
    ]