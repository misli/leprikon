# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-01-12 22:17
from __future__ import unicode_literals

from django.db import migrations
import leprikon.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('leprikon', '0023_registration_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='club',
            name='price',
            field=leprikon.models.fields.PriceField(blank=True, decimal_places=0, max_digits=10, null=True, verbose_name='price'),
        ),
        migrations.AlterField(
            model_name='event',
            name='price',
            field=leprikon.models.fields.PriceField(blank=True, decimal_places=0, max_digits=10, null=True, verbose_name='price'),
        ),
    ]