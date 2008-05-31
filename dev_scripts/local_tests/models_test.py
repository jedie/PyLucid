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

# Use the models from the test plugin
from tests.unittest_plugin.unittest_plugin import TestArtist, TestAlbum


print "-----------------------------------------------------------------------"

print "XXX"
print TestAlbum._meta.app_label
#t = TestAlbum._meta
#for i in dir(t):
#    print i, getattr(t, i)


print "-----------------------------------------------------------------------"
try:
    # Here the table doesn't exist
    m = TestArtist(name = "foobar")
    m.save()
except Exception, err:
    print err

print "-----------------------------------------------------------------------"

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

def get_create_table2(*plugin_models):
    from django.conf import settings
    from django.core.management.color import no_style
    style = no_style()
    from django.core.management import sql
    from django.db import models

    models.loading.register_models("PyLucidPlugins", *plugin_models)

    # get all delete statements for the given App
    app = models.get_app("PyLucidPlugins")
    statements = sql.sql_create(app, style)

    #cleanup
    app_models = models.loading.cache.app_models
    del(app_models["PyLucidPlugins"])
#    settings.INSTALLED_APPS = old_inst_apps

    return statements

statements = get_create_table(models = (TestArtist, TestAlbum))
#statements = get_create_table2(TestArtist, TestAlbum)

from django.db import connection
cursor = connection.cursor()
for statement in statements:
    print repr(statement)
    cursor.execute(statement)

print "-----------------------------------------------------------------------"

# Now we can use the created tables
m = TestArtist(name = "foobar")
m.save()
a = TestAlbum(
    artist = m,
    name = "jup",
    num_stars = 12,
)
a.save()
print TestAlbum.objects.all().values()

print "-----------------------------------------------------------------------"

# Not needed to "insert" the models:
#from PyLucid.system.PyLucidPlugins import models as PluginModels
#PluginModels.TestArtist = TestArtist
#PluginModels.TestAlbum = TestAlbum

def get_delete_sql(*plugin_models):
    from django.conf import settings
    from django.core.management.color import no_style
    style = no_style()
    from django.core.management import sql
    from django.db import models

#    # Insert app in installed apps
#    old_inst_apps = settings.INSTALLED_APPS
#    inst_apps = list(old_inst_apps)
#    inst_apps.append("PyLucid.system.PyLucidPlugins")
#    settings.INSTALLED_APPS = inst_apps

    models.loading.register_models("PyLucidPlugins", *plugin_models)

    # get all delete statements for the given App
    app = models.get_app("PyLucidPlugins")
    statements = sql.sql_delete(app, style)

    #cleanup
    app_models = models.loading.cache.app_models
    del(app_models["PyLucidPlugins"])
#    settings.INSTALLED_APPS = old_inst_apps

    return statements

statements = get_delete_sql(TestArtist)
print "1:", statements

statements = get_delete_sql(TestArtist, TestAlbum)
print "2:", statements

# Delete the tables...
from django.db import connection
cursor = connection.cursor()
for statement in statements:
    cursor.execute(statement)

# After this no tables left:
statements = get_delete_sql(TestArtist, TestAlbum)
print statements

statements = get_delete_sql(TestAlbum)
print statements

print "-----------------------------------------------------------------------"

# No tables error:
try:
    m = TestArtist(name = "foobar")
    m.save()
except Exception, err:
    print err

print " - END -"