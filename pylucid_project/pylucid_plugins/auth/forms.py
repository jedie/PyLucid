# coding: utf-8


from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from pylucid_project.utils import crypt
from pylucid_project.apps.pylucid.models import UserProfile

class WrongUserError(Exception):
    pass

class UsernameForm(forms.Form):
    username = forms.CharField(max_length=_('30'), label=_('Username'),
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


class ShaLoginForm(UsernameForm):
    """
    Form for the SHA1-JavaScript-Login.
    """
    sha_a2 = forms.CharField(min_length=crypt.HASH_LEN, max_length=crypt.HASH_LEN)
    sha_b = forms.CharField(min_length=crypt.HASH_LEN / 2, max_length=crypt.HASH_LEN / 2)

    def clean_sha_a2(self):
        sha_a2 = self.cleaned_data["sha_a2"]
        if crypt.validate_sha_value(sha_a2) != True:
            raise forms.ValidationError(u"sha_a2 is not valid SHA value.")

        return sha_a2

    def clean_sha_b(self):
        """
        The sha_b value is only a part of a SHA1 hexdigest. So we need to add
        some characers to use the rypt.validate_sha_value() method.
        """
        sha_b = self.cleaned_data["sha_b"]

        # Fill with null, to match the full SHA1 hexdigest length.
        fill_len = crypt.HASH_LEN - (crypt.HASH_LEN / 2)
        temp_value = ("0" * fill_len) + sha_b

        if crypt.validate_sha_value(temp_value) != True:
            raise forms.ValidationError(u"sha_b is not a valid SHA value.")

        return sha_b

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
