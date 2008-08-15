# -*- coding: utf-8 -*-
"""
    PyLucid.models.JS_LoginData
    ~~~~~~~~~~~~~~~~~~~

    SHA information for the PyLucid JS-SHA-Login.

    Note: We make a Monkey-Patch (?) and change the method set_password() from
    the model class django.contrib.auth.models.User. TODO: Change this.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.db import models
from django.contrib import admin
from django.core.cache import cache
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Group, UNUSABLE_PASSWORD

from PyLucid.tools import crypt

class JS_LoginData(models.Model):
    """
    SHA information for the PyLucid JS-SHA-Login.
    """
    user = models.ForeignKey(User)

    sha_checksum = models.CharField(max_length=192)
    salt = models.CharField(max_length=5)

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)

    def set_unusable_password(self):
        self.salt = UNUSABLE_PASSWORD
        self.sha_checksum = UNUSABLE_PASSWORD

    def set_password(self, raw_password):
        raw_password = str(raw_password)
        salt, sha_checksum = crypt.make_sha_checksum2(raw_password)
        self.salt = salt
        self.sha_checksum = sha_checksum

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = verbose_name_plural = 'JS-LoginData'
        db_table = 'PyLucid_js_logindata'
        app_label = 'PyLucid'


class JS_LoginDataAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'sha_checksum', 'salt', 'createtime', 'lastupdatetime'
    )

admin.site.register(JS_LoginData, JS_LoginDataAdmin)

#______________________________________________________________________________

# Save the original method
old_set_password = User.set_password

def set_password(user, raw_password):
    #    print "set_password() debug:", user, raw_password
    if user.id == None:
        # It is a new user. We must save the django user accound first to get a
        # existing user object with a ID and then the JS_LoginData can assign to it.
        user.save()

    # Save the password for the JS-SHA-Login:
    login_data, status = JS_LoginData.objects.get_or_create(user = user)
    login_data.set_password(raw_password)
    login_data.save()

    # Use the original method to set the django User password:
    old_set_password(user, raw_password)


# Make a hook into Django's default way to set a new User Password.
# Get the new raw_password and set the PyLucid password, too.
User.set_password = set_password
