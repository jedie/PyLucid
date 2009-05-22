# coding: utf-8

"""
    PyLucid auth backends
    ~~~~~~~~~~~~~~~~~~~~~

    SiteAuthBackend: Limit access to sites via UserProfile

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import warnings

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.auth.backends import ModelBackend


class SiteAuthBackend(ModelBackend):
    def authenticate(self, username=None, password=None):       
        try:
            user = User.objects.get(username=username)
            if not user.check_password(password):
                if settings.DEBUG:
                    warnings.warn("Wrong password!")
                return None
        except User.DoesNotExist, err:
            if settings.DEBUG:
                warnings.warn("User %s doesn't exist: %s" % (username, err))
            return None
    
        if settings.DEBUG:
            warnings.warn("Username %s and password ok." % username)
               
        if user.is_superuser:
            if settings.DEBUG:
                warnings.warn("Superuser can access all sites.")
            return user
        else:
            if settings.DEBUG:
                warnings.warn("No superuser -> check UserProfile.")
        
        try:
            user_profile = user.get_profile()
        except Exception, err:
            warnings.warn("Error getting user profile: %s" % err)
            return None
        
        current_site = Site.objects.get_current()
        sites = user_profile.site.all()
        if current_site in sites:
            if settings.DEBUG:
                warnings.warn("User can access these site.")
            return user
        else:
            warnings.warn("You can't access these site!") 
            return None