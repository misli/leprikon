# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-02-05 09:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leprikon', '0041_billing_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='chat_group_type',
            field=models.CharField(blank=True, choices=[('B', 'broadcast group'), ('C', 'chat group')], help_text='Only the leader can write to broadcast group. Users may reply to the sender with direct messages.\nChat group allows all members to chat with each other.', max_length=1, null=True, verbose_name='chat group type'),
        ),
        migrations.AddField(
            model_name='subjecttype',
            name='chat_group_type',
            field=models.CharField(choices=[('B', 'broadcast group'), ('C', 'chat group')], default='B', help_text='Only the leader can write to broadcast group. Users may reply to the sender with direct messages.\nChat group allows all members to chat with each other.', max_length=1, verbose_name='default chat group type'),
        ),
    ]