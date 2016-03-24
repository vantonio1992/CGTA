# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-20 10:07
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('CGTA', '0005_auto_20160220_1839'),
    ]

    operations = [
        migrations.RenameField(
            model_name='document',
            old_name='output',
            new_name='output_image',
        ),
        migrations.RemoveField(
            model_name='document',
            name='input',
        ),
        migrations.AddField(
            model_name='document',
            name='input_image',
            field=models.ImageField(default=datetime.datetime(2016, 2, 20, 10, 7, 12, 62000, tzinfo=utc), upload_to=b'input/%Y/%m/%d'),
            preserve_default=False,
        ),
    ]
