# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2018-04-02 19:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leprikon', '0010_subject_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='subjectregistration',
            name='payment_requested',
            field=models.DateTimeField(editable=False, null=True, verbose_name='payment request time'),
        ),
    ]
