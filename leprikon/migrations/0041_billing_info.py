# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-01-29 22:16
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import leprikon.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('leprikon', '0040_due_dates'),
    ]

    operations = [
        migrations.CreateModel(
            name='BillingInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('street', models.CharField(blank=True, max_length=150, null=True, verbose_name='street')),
                ('city', models.CharField(blank=True, max_length=150, null=True, verbose_name='city')),
                ('postal_code', leprikon.models.fields.PostalCodeField(blank=True, null=True, verbose_name='postal code')),
                ('company_num', models.CharField(blank=True, max_length=8, null=True, verbose_name='company number')),
                ('vat_number', models.CharField(blank=True, max_length=10, null=True, verbose_name='VAT number')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leprikon_billing_info', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'billing information',
                'verbose_name_plural': 'billing information',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='SubjectRegistrationBillingInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('street', models.CharField(blank=True, max_length=150, null=True, verbose_name='street')),
                ('city', models.CharField(blank=True, max_length=150, null=True, verbose_name='city')),
                ('postal_code', leprikon.models.fields.PostalCodeField(blank=True, null=True, verbose_name='postal code')),
                ('company_num', models.CharField(blank=True, max_length=8, null=True, verbose_name='company number')),
                ('vat_number', models.CharField(blank=True, max_length=10, null=True, verbose_name='VAT number')),
                ('registration', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='billing_info', to='leprikon.SubjectRegistration', verbose_name='registration')),
            ],
            options={
                'verbose_name': 'billing information',
                'verbose_name_plural': 'billing information',
            },
        ),
    ]