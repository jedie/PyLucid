#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Standalone django test with a 'memory-only-django-installation'.

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

#______________________________________________________________________________
# Test app code:

from django import forms
from django.contrib.auth.models import User
class UsernameForm(forms.ModelForm):
    def validate_unique(self):
        pass
    class Meta:
        model = User
        fields=("username",)

#------------------------------------------------------------------------------
if __name__ == "__main__":
    print "- create the model tables...",
    from django.core import management
    management.call_command('syncdb', verbosity=1, interactive=False)
    print "OK"
    print "-"*80

    #__________________________________________________________________________
    # Test code:
     
    User.objects.create_superuser(username="test", email="", password="test")
    
    f = UsernameForm({u'username': u'test'})
    print f.is_valid()
    print f.errors

    print "-"*80    
    print "- END -"