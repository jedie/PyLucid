# coding: utf-8

"""
    pylucid.models.Page
    ~~~~~~~~~~~~~~~~~~~

    New PyLucid models since v0.9

    TODO:
        Where to store bools like: showlinks, permitViewPublic ?

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.db import models
from django.db.models import signals
from django.contrib.auth.models import User

from pylucid_project.utils import crypt

from pylucid_project.apps.pylucid.models.base_models import UpdateInfoBaseModel, AutoSiteM2M
from pylucid_project.apps.pylucid.shortcuts import failsafe_message

from pylucid_project.pylucid_plugins import update_journal


TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"







class UserProfile(AutoSiteM2M, UpdateInfoBaseModel):
    """
    Stores additional information about PyLucid users
    http://docs.djangoproject.com/en/dev/topics/auth/#storing-additional-information-about-users

    Created via post_save signal, if a new user created.

    inherited attributes from AutoSiteM2M:
        sites   -> ManyToManyField to Site
        on_site -> sites.managers.CurrentSiteManager instance
        
    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    user = models.ForeignKey(User, unique=True, related_name="%(class)s_user")

    sha_login_checksum = models.CharField(max_length=192,
        help_text="Checksum for PyLucid JS-SHA-Login"
    )
    sha_login_salt = models.CharField(max_length=5,
        help_text="Salt value for PyLucid JS-SHA-Login"
    )

    # TODO: Overwrite help_text:
#    sites = models.ManyToManyField(Site,
#        help_text="User can access only these sites."
#    )

    def set_sha_login_password(self, raw_password):
        """
        create salt+checksum for JS-SHA-Login.
        see also: http://www.pylucid.org/_goto/8/JS-SHA-Login/
        """
        raw_password = str(raw_password)
        salt, sha_checksum = crypt.make_sha_checksum2(raw_password)
        self.sha_login_salt = salt
        self.sha_login_checksum = sha_checksum
        failsafe_message("SHA Login salt+checksum set for user '%s'." % self.user)

    def __unicode__(self):
        sites = self.sites.values_list('name', flat=True)
        return u"UserProfile for user '%s' (on sites: %r)" % (self.user.username, sites)

    class Meta:
        app_label = 'pylucid'
        ordering = ("user",)

#______________________________________________________________________________
# Create user profile via signals

def create_user_profile(sender, **kwargs):
    """ signal handler: creating user profile, after a new user created. """
    user = kwargs["instance"]

    userprofile, created = UserProfile.objects.get_or_create(user=user)
    if created:
        failsafe_message("UserProfile entry for user '%s' created." % user)
#
#        if not user.is_superuser: # Info: superuser can automaticly access all sites
#            site = Site.objects.get_current()
#            userprofile.site.add(site)
#            failsafe_message("Add site '%s' to '%s' UserProfile." % (site.name, user))

signals.post_save.connect(create_user_profile, sender=User)


#______________________________________________________________________________
"""
We make a Monkey-Patch and change the method set_password() from
the model class django.contrib.auth.models.User.
We need the raw plaintext password, this is IMHO not available via signals.
"""

# Save the original method
orig_set_password = User.set_password


def set_password(user, raw_password):
    #print "set_password() debug:", user, raw_password
    if user.id == None:
        # It is a new user. We must save the django user accound first to get a
        # existing user object with a ID and then the JS-SHA-Login Data can assign to it.
        user.save()

    # Use the original method to set the django User password:
    orig_set_password(user, raw_password)

    userprofile, created = UserProfile.objects.get_or_create(user=user)
    if created:
        failsafe_message("UserProfile entry for user '%s' created." % user)

    # Save the password for the JS-SHA-Login:
    userprofile.set_sha_login_password(raw_password)
    userprofile.save()


# replace the method
User.set_password = set_password
