# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2018-01-16 13:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leprikon', '0007_bill_print_setup'),
    ]

    operations = [
        migrations.AddField(
            model_name='leprikonsite',
            name='company_name',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='company name'),
        ),
    ]