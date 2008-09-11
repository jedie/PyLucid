#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Standalone django model test with a 'memory-only-django-installation'.
You can play with a django model without a complete django app installation.
http://www.djangosnippets.org/snippets/1044/ (en)
http://www.jensdiemer.de/_command/118/blog/detail/16/ (de)
http://www.python-forum.de/topic-15649.html (de) 
"""

import os

os.chdir("../pylucid_project/") # Goto where django exist, optional

APP_LABEL = os.path.splitext(os.path.basename(__file__))[0]

os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"
from django.conf import global_settings

global_settings.INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    APP_LABEL,
)
global_settings.DATABASE_ENGINE = "sqlite3"
global_settings.DATABASE_NAME = ":memory:"

from django.core.management import sql
from django.db import models, connection

from django.core.management.color import no_style
STYLE = no_style()

def create_table(*models):
    """ Create all tables for the given models """
    cursor = connection.cursor()
    def execute(statements):
        for statement in statements:
            cursor.execute(statement)

    for model in models:
        execute(connection.creation.sql_create_model(model, STYLE)[0])
        execute(connection.creation.sql_indexes_for_model(model, STYLE))
        execute(sql.custom_sql_for_model(model, STYLE))
        execute(connection.creation.sql_for_many_to_many(model, STYLE))

#______________________________________________________________________________
# Test model classes:

from django.db import models

class Test(models.Model):
    my_id = models.CharField(max_length=32, primary_key = True)
    text = models.TextField()

    def __unicode__(self):
        return u"Test entry: '%s'" % self.text

    class Meta:
        app_label = APP_LABEL

#------------------------------------------------------------------------------
if __name__ == "__main__":
    print "- create the model tables...",
    from django.core import management
    management.call_command('syncdb', verbosity=1, interactive=False)
    print "OK"

    create_table(Test)
    print "-"*80
    
    #__________________________________________________________________________
    # Test code:
    
    instance = Test(text="test")
    print instance
    for field in instance._meta.fields:
        print field, field.name
    
    print instance._meta.pk
    
#    for i in dir(instance._meta):
#        print i, getattr(instance, i, "--")
    
    print "-"*80
    print "- END -"