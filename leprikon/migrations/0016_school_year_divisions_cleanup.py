# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-08-29 09:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leprikon', '0015_school_year_divisions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='periods',
        ),
        migrations.RemoveField(
            model_name='course',
            name='unit',
        ),
        migrations.RemoveField(
            model_name='schoolyearperiod',
            name='school_year',
        ),
        migrations.AlterField(
            model_name='course',
            name='school_year_division',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='leprikon.SchoolYearDivision', verbose_name='school year division'),
        ),
        migrations.AlterField(
            model_name='schoolyearperiod',
            name='school_year_division',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='periods', to='leprikon.SchoolYearDivision', verbose_name='school year division'),
        ),
    ]
