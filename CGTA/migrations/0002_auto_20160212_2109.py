# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-12 12:09
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('CGTA', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='docfile',
        ),
        migrations.AddField(
            model_name='document',
            name='sample_image',
            field=models.ImageField(default=datetime.datetime(2016, 2, 12, 12, 9, 12, 271000, tzinfo=utc), upload_to=b'documents/%Y/%m/%d'),
            preserve_default=False,
        ),
    ]
