# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import bot.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.IntegerField(primary_key=True, serialize=False)),
                ('state', bot.models.fields.SerializedField(null=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255, null=True)),
                ('username', models.CharField(max_length=255, null=True)),
            ],
        ),
    ]
