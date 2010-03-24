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
from django.utils.translation import ugettext as _
from django.contrib.auth.backends import ModelBackend

from pylucid_project.utils import crypt

from pylucid_project.apps.pylucid.shortcuts import failsafe_message
from pylucid_project.apps.pylucid.models import LogEntry


#LOCAL_DEBUG = True
LOCAL_DEBUG = False

if LOCAL_DEBUG:
    failsafe_message("Debug mode in auth_backends is on!", UserWarning)


def can_access_site(user):
    """
    Check if the user can access the current site.
    Use the UserProfile <-> site relationship.
    Skip check for all superusers.
    """
    if user.is_superuser:
        if LOCAL_DEBUG:
            failsafe_message("Superuser can access all sites.")
        return True
    else:
        if LOCAL_DEBUG:
            failsafe_message("No superuser -> check UserProfile.")

    try:
        user_profile = user.get_profile()
    except Exception, err:
        msg = _("Error getting user profile: %s") % err
        LogEntry.objects.log_action(app_label="pylucid", action="auth_backends", message=msg)
        failsafe_message(msg)
        return

    current_site = Site.objects.get_current()
    sites = user_profile.sites.all()
    if current_site in sites:
        if LOCAL_DEBUG:
            failsafe_message("User can access these site.")
        return True
    else:
        msg = _("You can't access these site!")
        LogEntry.objects.log_action(
            app_label="pylucid", action="auth_backends", message=msg,
            data={
                "user_username": user.username,
                "site:": current_site.name,
            }
        )
        failsafe_message(msg)
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
                    failsafe_message("Wrong password!")
                return
        except User.DoesNotExist, err:
            msg = _("User %(username)s doesn't exist: %(err)s") % {"username": username, "err":err}
            LogEntry.objects.log_action(
                app_label="pylucid", action="auth_backends", message=msg,
            )
            if LOCAL_DEBUG:
                raise
            if settings.DEBUG:
                failsafe_message()
            return

        if LOCAL_DEBUG:
            failsafe_message("Username %s and password ok." % username)

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
            LogEntry.objects.log_action(
                app_label="pylucid", action="auth_backends",
                message="User %r check_js_sha_checksum error: %s" % (user, err),
            )
            if LOCAL_DEBUG:
                raise
            if settings.DEBUG:
                failsafe_message(err)
            return None

        if check != True:
            # Wrong password
            LogEntry.objects.log_action(
                app_label="pylucid", action="auth_backends",
                message="User %r check_js_sha_checksum failed." % user,
            )
            return

        # Limit the access to UserProfile <-> site relationship
        if can_access_site(user) == True:
            return user
