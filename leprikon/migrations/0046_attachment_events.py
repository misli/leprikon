# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-02-13 16:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('leprikon', '0045_registration_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='subjectattachment',
            name='events',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('registration_received', 'registration received'), ('registration_approved', 'registration approved'), ('registration_refused', 'registration refused'), ('registration_payment_request', 'payment requested'), ('registration_canceled', 'registration canceled'), ('discount_granted', 'discount granted'), ('payment_received', 'payment received')], default=['registration_received'], help_text='The attachment will be sent with notification on selected events.', max_length=149, verbose_name='send when'),
        ),
        migrations.AddField(
            model_name='subjectattachment',
            name='public',
            field=models.BooleanField(default=True, help_text='The attachment will be available before registration.', verbose_name='public'),
        ),
        migrations.AddField(
            model_name='subjecttypeattachment',
            name='events',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('registration_received', 'registration received'), ('registration_approved', 'registration approved'), ('registration_refused', 'registration refused'), ('registration_payment_request', 'payment requested'), ('registration_canceled', 'registration canceled'), ('discount_granted', 'discount granted'), ('payment_received', 'payment received')], default=['registration_received'], help_text='The attachment will be sent with notification on selected events.', max_length=149, verbose_name='send when'),
        ),
        migrations.AddField(
            model_name='subjecttypeattachment',
            name='public',
            field=models.BooleanField(default=True, help_text='The attachment will be available before registration.', verbose_name='public'),
        ),
        migrations.AlterField(
            model_name='subjectattachment',
            name='events',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('registration_received', 'registration received'), ('registration_approved', 'registration approved'), ('registration_refused', 'registration refused'), ('registration_payment_request', 'payment requested'), ('registration_canceled', 'registration canceled'), ('discount_granted', 'discount granted'), ('payment_received', 'payment received')], default=[], help_text='The attachment will be sent with notification on selected events.', max_length=149, verbose_name='send when'),
        ),
        migrations.AlterField(
            model_name='subjecttypeattachment',
            name='events',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('registration_received', 'registration received'), ('registration_approved', 'registration approved'), ('registration_refused', 'registration refused'), ('registration_payment_request', 'payment requested'), ('registration_canceled', 'registration canceled'), ('discount_granted', 'discount granted'), ('payment_received', 'payment received')], default=[], help_text='The attachment will be sent with notification on selected events.', max_length=149, verbose_name='send when'),
        ),
    ]
