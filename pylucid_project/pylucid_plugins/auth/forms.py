# coding: utf-8

"""
    PyLucid JS-SHA-Login forms
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    A secure JavaScript SHA-1 AJAX Login.

    :copyleft: 2007-2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""


from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.forms.forms import NON_FIELD_ERRORS

from pylucid_project.utils import crypt
from pylucid_project.apps.pylucid.models import UserProfile
from django.forms.util import ErrorDict


class WrongUserError(Exception):
    pass


class HoneypotForm(forms.Form):
    username = forms.CharField(max_length=30, label=_('username'))
    password = forms.CharField(max_length=128, label=_('password'),
        widget=forms.PasswordInput
    )


class UsernameForm(forms.Form):
    username = forms.CharField(max_length=30, label=_('Username'),
        help_text=_('Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores).')
    )

    def get_user(self):
        username = self.cleaned_data["username"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist, e:
            raise WrongUserError("User %r doesn't exists!" % username)

        if not user.is_active:
            raise WrongUserError("User %r is not active!" % user)

        return user

    def get_user_profile(self, user=None):
        if user is None:
            user = self.get_user()
        try:
            return user.get_profile()
        except UserProfile.DoesNotExist, err:
            raise WrongUserError("Can't get user profile: %r" % err)

    def get_user_and_profile(self):
        user = self.get_user()
        user_profile = self.get_user_profile(user)
        return user, user_profile


class Sha1BaseForm(forms.Form):
    sha_a = forms.CharField(min_length=crypt.HASH_LEN, max_length=crypt.HASH_LEN)
    sha_b = forms.CharField(min_length=crypt.HASH_LEN / 2, max_length=crypt.HASH_LEN / 2)
    cnonce = forms.CharField(min_length=crypt.HASH_LEN, max_length=crypt.HASH_LEN)

    def _validate_sha1(self, sha_value, key):
        if crypt.validate_sha_value(sha_value) != True:
            raise forms.ValidationError(u"%s is not valid SHA value." % key)
        return sha_value

    def _validate_sha1_by_key(self, key):
        sha_value = self.cleaned_data[key]
        return self._validate_sha1(sha_value, key)

    def _validate_filled_sha1_by_key(self, key):
        value = self.cleaned_data[key]
        # Fill with null, to match the full SHA1 hexdigest length.
        temp_value = value.ljust(crypt.HASH_LEN, "0")
        self._validate_sha1(temp_value, key)
        return value

    def clean_sha_a(self):
        return self._validate_sha1_by_key("sha_a")
    def clean_cnonce(self):
        return self._validate_sha1_by_key("cnonce")

    def clean_sha_b(self):
        """
        The sha_b value is only a part of a SHA1 hexdigest. So we need to add
        some characers to use the crypt.validate_sha_value() method.
        """
        return self._validate_filled_sha1_by_key("sha_b")


class ShaLoginForm(Sha1BaseForm, UsernameForm):
    """
    Form for the SHA1-JavaScript-Login.

    inherited form Sha1BaseForm() this form fields:
        sha_a
        sha_b
        cnonce
    inherited form UsernameForm() this form fields:
        username
    """
    pass


class JSPasswordChangeForm(Sha1BaseForm):
    """
    Form for changing the password with Client side JS encryption.

    inherited form Sha1BaseForm() this form fields:
        sha_a
        sha_b
        cnonce
    for pre-verification with old password "JS-SHA1" values
    """
    # new password as salted SHA1 hash:
    salt = forms.CharField(min_length=crypt.SALT_LEN, max_length=crypt.SALT_LEN) # length see: hashers.SHA1PasswordHasher() and django.utils.crypto.get_random_string()
    sha1hash = forms.CharField(min_length=crypt.HASH_LEN, max_length=crypt.HASH_LEN)
    def clean_salt(self):
        return self._validate_filled_sha1_by_key("salt")
    def clean_sha1(self):
        return self._validate_sha1_by_key("sha1hash")

