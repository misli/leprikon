# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-07 16:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leprikon', '0003_managers'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='subjectregistration',
            unique_together=set([]),
        ),
    ]
