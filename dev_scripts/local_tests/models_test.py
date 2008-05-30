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

from django.db import models
from django.contrib.auth.models import User


class TestModel(models.Model):
    name = models.CharField(unique=True, max_length=150)
    content = models.TextField()

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)

    createby = models.ForeignKey(User, related_name="test_createby",
        null=True, blank=True
    )
    lastupdateby = models.ForeignKey(User, related_name="test_lastupdateby",
        null=True, blank=True
    )
    class Admin:
        pass

    class Meta:
        db_table = 'PyLucid_test'
        app_label = 'PyLucid'


print "-"*79
try:
    # Here the table doesn't exist
    TestModel(name="one", content="Test1").save()
except Exception, err:
    print err
print "-"*79


# Syncdb created the table
from django.core import management
management.call_command('syncdb', verbosity=1, interactive=False)

print "-"*79
# Now we can use the modes as normal models
TestModel(name="one", content="Test1").save()
TestModel(name="two", content="Test2").save()
print TestModel.objects.all()

print " - END -"