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
        # Fill with null, to match the full SHA1 hexdigest length.
        value = self.cleaned_data[key]

#        fill_len = crypt.HASH_LEN - len(value)
#        temp_value = ("0" * fill_len) + value

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
    salt = forms.CharField(min_length=crypt.SALT_LEN, max_length=crypt.SALT_LEN)
    sha1hash = forms.CharField(min_length=crypt.HASH_LEN, max_length=crypt.HASH_LEN)
    def clean_salt(self):
        return self._validate_filled_sha1_by_key("salt")
    def clean_sha1(self):
        return self._validate_sha1_by_key("sha1hash")

#
#class NewPasswordForm(forms.Form):
#    username = forms.CharField(
#        help_text="(required)", min_length=3, max_length=30
#    )
#
#    # Should normaly never be send back!
#    raw_password = forms.CharField(
#        help_text="(required)", required=False, widget=forms.PasswordInput()
#    )
#
#    sha_1 = forms.CharField(
#        label="SHA1 for django",
#        help_text="(automatic generated with JavaScript.)",
#        widget=forms.TextInput(attrs={"readonly":"readonly", "size":"40"}),
#        min_length=crypt.HASH_LEN, max_length=crypt.HASH_LEN
#    )
#    sha_2 = forms.CharField(
#        label="SHA1 for PyLucid",
#        help_text="(automatic generated with JavaScript.)",
#        widget=forms.TextInput(attrs={"readonly":"readonly", "size":"40"}),
#        min_length=crypt.HASH_LEN, max_length=crypt.HASH_LEN
#    )
#
#    #__________________________________________________________________________
#    # Validate the SHA1 hexdigest values:
#
#    def clean_sha_1(self):
#        return validate_sha1("sha_1", self.cleaned_data)
#
#    def clean_sha_2(self):
#        return validate_sha1("sha_2", self.cleaned_data)
#
#
##______________________________________________________________________________
## FORMS
#
##class BaseModelForm(forms.ModelForm):
##    """
##    A model form witch don't validate unique fields.
##
##    This ModelForm is only for generating the forms and not for create/update
##    any database data. So a field unique Test would like generate Errors like:
##        User with this Username already exists.
##
##    see also:
##    http://www.jensdiemer.de/_command/118/blog/detail/30/ (de)
##    http://www.python-forum.de/topic-16000.html (de)
##    """
##    def __init__(self, *args, **kwargs):
##        """ Change field meta in a DRY way """
##        super(BaseModelForm, self).__init__(*args, **kwargs)
##
##        self.model.full_validate = self._skip
##
##    def _skip(self, *args, **kwargs):
##        pass
##
##    def validate_unique(self):
##        pass
#
#class UsernameForm(forms.Form):
#    """
#    form for input the username, used in auth.login()
#    
#    FIXME: This is not DRY.
#    """
#
#
##    class Meta:
##        model = User
##        fields = ("username",)
#
#
#class PasswordForm(forms.Form):
#    """
#    form for input the username, used in auth._sha_login()
#    
#    FIXME: This is not DRY.
#    """
#    password = forms.CharField(max_length=_('128'), label=_('Password'), widget=forms.PasswordInput()
#    )
#
##    def __init__(self, *args, **kwargs):
##        """ Change field meta in a DRY way """
##        super(PasswordForm, self).__init__(*args, **kwargs)
##
##        self.fields['password'].widget = forms.PasswordInput()
##        self.fields['password'].help_text = ""
#
#    def is_valid(self, username):
#        is_valid = super(PasswordForm, self).is_valid()
#        if not is_valid:
#            return False
#
#        password = self.cleaned_data["password"]
#        self.user = auth.authenticate(username=username, password=password)
#        if not self.user:
#            self._errors["password"] = ("Wrong password!",)
#            return False
#
#        return True
#
##    class Meta:
##        model = User
##        fields = ("password",)
#
#
#class ResetForm(forms.Form):
#    """
#    from for input username and email, used in auth.pass_reset()
#    """
#    username = forms.CharField(max_length=_('30'), label=_('Username'),
#        help_text=_('Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores).')
#    )
#    email = forms.EmailField(max_length=_('75'), label=_('E-mail address'))
#
##    def __init__(self, *args, **kwargs):
##        super(ResetForm, self).__init__(*args, **kwargs)
##        # User.email is normaly a not required field, here it's required!
##        self.fields['email'].required = True
#
##    class Meta:
##        model = User
##        fields = ("username", "email")
