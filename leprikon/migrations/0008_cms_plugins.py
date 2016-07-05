# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-05 13:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0015_auto_20160421_0000'),
        ('leprikon', '0007_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClubPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('template', models.CharField(choices=[('default', 'Default')], default='default', help_text='The template used to render plugin.', max_length=100, verbose_name='template')),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leprikon.Club', verbose_name='club')),
            ],
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='EventPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('template', models.CharField(choices=[('default', 'Default')], default='default', help_text='The template used to render plugin.', max_length=100, verbose_name='template')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leprikon.Event', verbose_name='event')),
            ],
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='FilteredLeaderListPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('school_year', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='leprikon.SchoolYear', verbose_name='school year')),
            ],
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='LeaderListPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('template', models.CharField(choices=[('default', 'Default')], default='default', help_text='The template used to render plugin.', max_length=100, verbose_name='template')),
                ('club', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='leprikon.Club', verbose_name='club')),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='leprikon.Event', verbose_name='event')),
                ('school_year', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='leprikon.SchoolYear', verbose_name='school year')),
            ],
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='LeaderPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('template', models.CharField(choices=[('default', 'Default')], default='default', help_text='The template used to render plugin.', max_length=100, verbose_name='template')),
                ('leader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leprikon.Leader', verbose_name='leader')),
            ],
            bases=('cms.cmsplugin',),
        ),
        migrations.RenameModel(
            old_name='LeprikonClubListPlugin',
            new_name='ClubListPlugin',
        ),
        migrations.RenameModel(
            old_name='LeprikonEventListPlugin',
            new_name='EventListPlugin',
        ),
        migrations.RenameModel(
            old_name='LeprikonFilteredClubListPlugin',
            new_name='FilteredClubListPlugin',
        ),
        migrations.RenameModel(
            old_name='LeprikonFilteredEventListPlugin',
            new_name='FilteredEventListPlugin',
        ),
    ]
