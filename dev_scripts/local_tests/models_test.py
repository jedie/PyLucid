#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A local django test with synced database but empty tables.
"""

from setup import setup
setup(
    path_info=False, extra_verbose=False,
    syncdb=True, insert_dump=False
)

#______________________________________________________________________________
# Test:

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User



class Musician(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    instrument = models.CharField(max_length=100)
    class Meta:
        # db_table is optional
#        db_table = 'PyLucid_test'
        app_label = 'PyLucid' # must be set to "PyLucid"

class Album(models.Model):
    artist = models.ForeignKey("Musician")
    name = models.CharField(max_length=100)
    num_stars = models.IntegerField()

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)

    createby = models.ForeignKey(User, related_name="test_createby",
        null=True, blank=True
    )
    lastupdateby = models.ForeignKey(User, related_name="test_lastupdateby",
        null=True, blank=True
    )
    class Meta:
        # db_table is optional
#        db_table = 'PyLucid_test'
        app_label = 'PyLucid' # must be set to "PyLucid"


print "------------------------------------------------------------------------------------------------------"
try:
    # Here the table doesn't exist
    m = Musician(first_name = "foo", last_name = "bar", instrument = "foobar")
    m.save()
except Exception, err:
    print err

print "------------------------------------------------------------------------------------------------------"

def get_create_table(models):
    from django.core.management.color import no_style
    style = no_style()
    from django.core.management import sql

    statements = []
    for model in models:
        statements += sql.sql_model_create(model, style)[0]
        statements += sql.sql_indexes_for_model(model, style)
        statements += sql.custom_sql_for_model(model)
    return statements

statements = get_create_table(models = (Musician, Album))

from django.db import connection
cursor = connection.cursor()
for statement in statements:
    print repr(statement)
    cursor.execute(statement)

print "------------------------------------------------------------------------------------------------------"

# Now we can use the created tables
m = Musician(first_name = "foo", last_name = "bar", instrument = "foobar")
m.save()
a = Album(
    artist = m,
    name = "jup",
    num_stars = 12,
)
a.save()
print Album.objects.all().values()

print "------------------------------------------------------------------------------------------------------"

# Not needed to "insert" the models:
#from PyLucid.system.PyLucidPlugins import models as PluginModels
#PluginModels.Musician = Musician
#PluginModels.Album = Album

def get_delete_sql(*plugin_models):
    from django.conf import settings
    from django.core.management.color import no_style
    style = no_style()
    from django.core.management import sql
    from django.db import models

    # Insert app in installed apps
    old_inst_apps = settings.INSTALLED_APPS
    inst_apps = list(old_inst_apps)
    inst_apps.append("PyLucid.system.PyLucidPlugins")
    settings.INSTALLED_APPS = inst_apps

    models.loading.register_models("PyLucidPlugins", *plugin_models)

    # get all delete statements for the given App
    app = models.get_app("PyLucidPlugins")
    statements = sql.sql_delete(app, style)

    #cleanup
    app_models = models.loading.cache.app_models
    del(app_models["PyLucidPlugins"])
    settings.INSTALLED_APPS = old_inst_apps

    return statements

statements = get_delete_sql(Musician)
print "1:", statements

statements = get_delete_sql(Musician, Album)
print "2:", statements

# Delete the tables...
from django.db import connection
cursor = connection.cursor()
for statement in statements:
    cursor.execute(statement)

# After this no tables left:
statements = get_delete_sql(Musician, Album)
print statements

statements = get_delete_sql(Album)
print statements

print "------------------------------------------------------------------------------------------------------"

# No tables error:
try:
    m = Musician(first_name = "foo", last_name = "bar", instrument = "foobar")
    m.save()
except Exception, err:
    print err

print " - END -"