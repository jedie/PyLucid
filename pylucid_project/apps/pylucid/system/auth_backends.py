# coding: utf-8

"""
    PyLucid auth backends
    ~~~~~~~~~~~~~~~~~~~~~
    
    Limit user access to sites via UserProfile

    SiteAuthBackend:
        for normal username/plaintext password
        
    SiteSHALoginAuthBackend:
        for JS-SHA1-Login
    

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.auth.backends import ModelBackend

from pylucid_project.utils import crypt
from pylucid.shortcuts import page_msg_or_warn


#LOCAL_DEBUG = True
LOCAL_DEBUG = False

if LOCAL_DEBUG:
    page_msg_or_warn("Debug mode in auth_backends is on!", UserWarning)


def can_access_site(user):
    """
    Check if the user can access the current site.
    Use the UserProfile <-> site relationship.
    Skip check for all superusers.
    """
    if user.is_superuser:
        if LOCAL_DEBUG:
            page_msg_or_warn("Superuser can access all sites.")
        return True
    else:
        if LOCAL_DEBUG:
            page_msg_or_warn("No superuser -> check UserProfile.")

    try:
        user_profile = user.get_profile()
    except Exception, err:
        page_msg_or_warn("Error getting user profile: %s" % err)
        return

    current_site = Site.objects.get_current()
    sites = user_profile.site.all()
    if current_site in sites:
        if LOCAL_DEBUG:
            page_msg_or_warn("User can access these site.")
        return True
    else:
        page_msg_or_warn("You can't access these site!")
        return


class SiteAuthBackend(ModelBackend):
    """
    Normal username/plaintext password authentication, but we limit user to sites.
    """
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username=username)
            if not user.check_password(password):
                if settings.DEBUG or LOCAL_DEBUG:
                    page_msg_or_warn("Wrong password!")
                return
        except User.DoesNotExist, err:
            if LOCAL_DEBUG:
                raise
            if settings.DEBUG:
                page_msg_or_warn("User %s doesn't exist: %s" % (username, err))
            return

        if LOCAL_DEBUG:
            page_msg_or_warn("Username %s and password ok." % username)

        # Limit the access to UserProfile <-> site relationship
        if can_access_site(user) == True:
            return user



class SiteSHALoginAuthBackend(ModelBackend):
    """
    Used for PyLucid JS-SHA-Login.
    Check challenge and limit access to sites.
    """
    def authenticate(self, user=None, challenge=None, sha_a2=None, sha_b=None, sha_checksum=None):
        if user == None: # Nothing to do: Normal auth?
            return

        try:
            check = crypt.check_js_sha_checksum(challenge, sha_a2, sha_b, sha_checksum)
        except crypt.SaltHashError, err:
            # Wrong password
            if LOCAL_DEBUG:
                raise
            if settings.DEBUG:
                page_msg_or_warn(err)
            return None

        if check != True:
            # Wrong password
            return

        # Limit the access to UserProfile <-> site relationship
        if can_access_site(user) == True:
            return user
