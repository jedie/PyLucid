# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_auto_20140926_2347'),
    ]

    operations = [
        migrations.CreateModel(
            name='ToDoPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, serialize=False, primary_key=True, to='cms.CMSPlugin', parent_link=True)),
                ('code', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
