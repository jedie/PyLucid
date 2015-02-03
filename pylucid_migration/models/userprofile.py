# coding: utf-8

"""
    pylucid.models
    ~~~~~~~~~~~~~~

    :copyleft: 2009-2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.db import models
from django.db.models import signals
from django.contrib.auth.models import User

# http://code.google.com/p/django-tools/
from django_tools.utils.messages import failsafe_message
from django_tools.models import UpdateInfoBaseModel

from pylucid_migration.base_models.many2many import AutoSiteM2M


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
    sha_login_salt = models.CharField(max_length=36,
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
        app_label = u'pylucid_migration'
        db_table = u'pylucid_userprofile'
        ordering = ("user",)

