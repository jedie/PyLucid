# coding: utf-8


from django import forms
from django.contrib import auth
from django.contrib.auth.models import User

from pylucid_project.utils import crypt



def get_newforms_data(key_name, cleaned_data):
    if not key_name in cleaned_data:
        raise forms.ValidationError(u"No '%s' data in the form." % key_name)
    return cleaned_data[key_name]


def validate_sha1(key_name, cleaned_data):
    """
    A universal routine to validate a SHA1 hexdigest for newforms.
    """
    sha_value = get_newforms_data(key_name, cleaned_data)

    if crypt.validate_sha_value(sha_value) == True:
        return sha_value
    else:
        raise forms.ValidationError(u"Wrong '%s' data." % key_name)


class SHA_LoginForm(forms.Form):
    """
    Form for the SHA1-JavaScript-Login.
    """
    sha_a2 = forms.CharField(
        min_length=crypt.HASH_LEN, max_length=crypt.HASH_LEN
    )
    sha_b = forms.CharField(
        min_length=crypt.HASH_LEN/2, max_length=crypt.HASH_LEN/2
    )

    #__________________________________________________________________________
    # Validate the SHA1 hexdigest values:

    def clean_sha_a2(self):
        return validate_sha1("sha_a2", self.cleaned_data)

    def clean_sha_b(self):
        """
        The sha_b value is only a part of a SHA1 hexdigest. So we need to add
        some characers to use the rypt.validate_sha_value() method.
        """
        sha_value = get_newforms_data("sha_b", self.cleaned_data)

        # Fill with null, to match the full SHA1 hexdigest length.
        fill_len = crypt.HASH_LEN - (crypt.HASH_LEN/2)
        temp_value = ("0" * fill_len) + sha_value

        if crypt.validate_sha_value(temp_value) == True:
            return sha_value
        else:
            raise forms.ValidationError(u"Wrong sha_b data.")


class NewPasswordForm(forms.Form):
    username = forms.CharField(
        help_text="(required)", min_length=3, max_length=30
    )

    # Should normaly never be send back!
    raw_password = forms.CharField(
        help_text="(required)", required=False, widget = forms.PasswordInput()
    )

    sha_1 = forms.CharField(
        label="SHA1 for django",
        help_text="(automatic generated with JavaScript.)",
        widget = forms.TextInput(attrs={"readonly":"readonly", "size":"40"}),
        min_length=crypt.HASH_LEN, max_length=crypt.HASH_LEN
    )
    sha_2 = forms.CharField(
        label="SHA1 for PyLucid",
        help_text="(automatic generated with JavaScript.)",
        widget = forms.TextInput(attrs={"readonly":"readonly", "size":"40"}),
        min_length=crypt.HASH_LEN, max_length=crypt.HASH_LEN
    )

    #__________________________________________________________________________
    # Validate the SHA1 hexdigest values:

    def clean_sha_1(self):
        return validate_sha1("sha_1", self.cleaned_data)

    def clean_sha_2(self):
        return validate_sha1("sha_2", self.cleaned_data)


#______________________________________________________________________________
# FORMS

class BaseModelForm(forms.ModelForm):
    """
    A model form witch don't validate unique fields.

    This ModelForm is only for generating the forms and not for create/update
    any database data. So a field unique Test would like generate Errors like:
        User with this Username already exists.

    see also:
    http://www.jensdiemer.de/_command/118/blog/detail/30/ (de)
    http://www.python-forum.de/topic-16000.html (de)
    """
    def validate_unique(self):
        pass


class UsernameForm(BaseModelForm):
    """
    form for input the username, used in auth.login()
    """   
    def is_valid(self):
        """ do a secont validation: try to get the user from database and
        check if he is active """        
        is_valid = super(UsernameForm, self).is_valid()
        if not is_valid:
            return False
        
        username = self.cleaned_data["username"]
        try:
            self.user = User.objects.get(username = username)
        except User.DoesNotExist, e:
            self._errors["username"] = ("User doesn't exist!",)
            return False
    
        return True
        
    class Meta:
        model = User
        fields=("username",)


class PasswordForm(BaseModelForm):
    """
    form for input the username, used in auth._sha_login()
    """
    def __init__(self, *args, **kwargs):
        """ Change field meta in a DRY way """
        super(PasswordForm, self).__init__(*args, **kwargs)

        self.fields['password'].widget = forms.PasswordInput()
        self.fields['password'].help_text = ""

    def is_valid(self, username):
        is_valid = super(PasswordForm, self).is_valid()
        if not is_valid:
            return False
        
        password = self.cleaned_data["password"]
        self.user = auth.authenticate(username=username, password=password)
        if not self.user:
            self._errors["password"] = ("Wrong password!",)
            return False
        
        return True

    class Meta:
        model = User
        fields=("password",)


class ResetForm(BaseModelForm):
    """
    from for input username and email, used in auth.pass_reset()
    """
    def __init__(self, *args, **kwargs):
        super(ResetForm, self).__init__(*args, **kwargs)
        # User.email is normaly a not required field, here it's required!
        self.fields['email'].required = True
        
    class Meta:
        model = User
        fields=("username","email")