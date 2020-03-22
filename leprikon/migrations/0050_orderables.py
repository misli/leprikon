# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-03-22 08:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import leprikon.models.fields
import leprikon.models.subjects


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0022_auto_20180620_1551'),
        ('leprikon', '0049_target_groups_fix'),
    ]

    operations = [
        migrations.CreateModel(
            name='FilteredOrderableListPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='leprikon_filteredorderablelistplugin', serialize=False, to='cms.CMSPlugin')),
            ],
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='Orderable',
            fields=[
                ('subject_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='leprikon.Subject')),
                ('duration', models.DurationField(verbose_name='duration')),
                ('due_from_days', models.IntegerField(blank=True, help_text='If set, payment request will be sent this number of days before start. If not set, payment request will be sent when registration is approved.', null=True, verbose_name='number of days to send the payment request before start')),
                ('due_date_days', models.IntegerField(default=0, verbose_name='number of days to due date before start')),
            ],
            options={
                'verbose_name': 'orderable event',
                'verbose_name_plural': 'orderable events',
                'ordering': ('code', 'name'),
            },
            bases=('leprikon.subject',),
        ),
        migrations.CreateModel(
            name='OrderableDiscount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accounted', models.DateTimeField(default=django.utils.timezone.now, verbose_name='accounted time')),
                ('amount', leprikon.models.fields.PriceField(decimal_places=0, default=0, max_digits=10, verbose_name='discount')),
                ('explanation', models.CharField(blank=True, default='', max_length=250, verbose_name='discount explanation')),
            ],
            options={
                'verbose_name': 'orderable event discount',
                'verbose_name_plural': 'orderable event discounts',
                'ordering': ('accounted',),
            },
            bases=(leprikon.models.subjects.TransactionMixin, models.Model),
        ),
        migrations.CreateModel(
            name='OrderableListPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='leprikon_orderablelistplugin', serialize=False, to='cms.CMSPlugin')),
                ('template', models.CharField(choices=[('default', 'Default'), ('grouped', 'Grouped by event groups')], default='default', help_text='The template used to render plugin.', max_length=100, verbose_name='template')),
                ('age_groups', models.ManyToManyField(blank=True, help_text='Keep empty to skip searching by age groups.', related_name='_orderablelistplugin_age_groups_+', to='leprikon.AgeGroup', verbose_name='age groups')),
                ('departments', models.ManyToManyField(blank=True, help_text='Keep empty to skip searching by departments.', related_name='_orderablelistplugin_departments_+', to='leprikon.Department', verbose_name='departments')),
            ],
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='OrderablePlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='leprikon_orderableplugin', serialize=False, to='cms.CMSPlugin')),
                ('template', models.CharField(choices=[('default', 'Default')], default='default', help_text='The template used to render plugin.', max_length=100, verbose_name='template')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='leprikon.Orderable', verbose_name='event')),
            ],
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='OrderableRegistration',
            fields=[
                ('subjectregistration_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='leprikon.SubjectRegistration')),
                ('start_date', models.DateField(verbose_name='start date')),
                ('start_time', models.TimeField(blank=True, null=True, verbose_name='start time')),
            ],
            options={
                'verbose_name': 'orderable event registration',
                'verbose_name_plural': 'orderable event registrations',
            },
            bases=('leprikon.subjectregistration',),
        ),
        migrations.AlterField(
            model_name='subjecttype',
            name='subject_type',
            field=models.CharField(choices=[('course', 'course'), ('event', 'event'), ('orderable', 'orderable event')], max_length=10, verbose_name='subjects'),
        ),
        migrations.AddField(
            model_name='orderablelistplugin',
            name='event_types',
            field=models.ManyToManyField(blank=True, help_text='Keep empty to skip searching by event types.', related_name='_orderablelistplugin_event_types_+', to='leprikon.SubjectType', verbose_name='event types'),
        ),
        migrations.AddField(
            model_name='orderablelistplugin',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='Keep empty to skip searching by groups.', related_name='_orderablelistplugin_groups_+', to='leprikon.SubjectGroup', verbose_name='event groups'),
        ),
        migrations.AddField(
            model_name='orderablelistplugin',
            name='leaders',
            field=models.ManyToManyField(blank=True, help_text='Keep empty to skip searching by leaders.', related_name='_orderablelistplugin_leaders_+', to='leprikon.Leader', verbose_name='leaders'),
        ),
        migrations.AddField(
            model_name='orderablelistplugin',
            name='school_year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='leprikon.SchoolYear', verbose_name='school year'),
        ),
        migrations.AddField(
            model_name='orderablelistplugin',
            name='target_groups',
            field=models.ManyToManyField(blank=True, help_text='Keep empty to skip searching by target groups.', related_name='_orderablelistplugin_target_groups_+', to='leprikon.TargetGroup', verbose_name='target groups'),
        ),
        migrations.AddField(
            model_name='orderablediscount',
            name='registration',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discounts', to='leprikon.OrderableRegistration', verbose_name='registration'),
        ),
        migrations.AddField(
            model_name='filteredorderablelistplugin',
            name='event_types',
            field=models.ManyToManyField(related_name='_filteredorderablelistplugin_event_types_+', to='leprikon.SubjectType', verbose_name='event types'),
        ),
        migrations.AddField(
            model_name='filteredorderablelistplugin',
            name='school_year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='leprikon.SchoolYear', verbose_name='school year'),
        ),
    ]
