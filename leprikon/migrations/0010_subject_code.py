# Generated by Django 1.9.13 on 2018-03-18 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leprikon', '0009_subjectpayment_received_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='code',
            field=models.PositiveSmallIntegerField(blank=True, default=0, verbose_name='accounting code'),
        ),
    ]
