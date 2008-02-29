#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    PyLucid JS-SHA-Login
    ~~~~~~~~~~~~~~~~~~~~

    A secure JavaScript SHA-1 Login and a plaintext fallback login.

    two steps
    ~~~~~~~~~
    We split the login into two steps:
        - step-1 -> input the username
        - step-2 -> input the password

    the "next_url"
    ~~~~~~~~~~~~~~
    The "next_url" is for a redirect after a login. It's optional.
    If there doesn't exist a "next_url" information, PyLucid displayed the
    current page. In every _command URL is the current page ID.

    The "next_url" is in the first step (input the username) a GET parameter.
    e.g.: localhost/_command/1/auth/login/?next=/ExamplePages/not-viewable
    Then, the "next_url" information went into the form and comes back in the
    POST data.

    TODO
    ~~~~
    Clearing the session table?
    http://www.djangoproject.com/documentation/sessions/#clearing-the-session-table

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    LastChangedDate: $LastChangedDate$
    Revision.......: $Rev$
    Author.........: $Author$

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE for more details
"""

__version__ = "$Rev$"

import datetime, posixpath

from django.http import HttpResponseRedirect
from django.core import mail
from django import newforms as forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext as _


# DEBUG is usefull for debugging password reset. It send no email, it puts the
# email text direclty into the CMS page.
#DEBUG = True
DEBUG = False
# IMPORTANT:
# Should realy only use for debugging!!!
if DEBUG:
    import warnings
    warnings.warn("Debugmode is on", UserWarning)


from django.conf import settings
from PyLucid.tools import crypt
from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.system.context_processors import add_dynamic_context
from PyLucid.models import JS_LoginData, Preference
from PyLucid.system.detect_page import get_default_page


class WrongPassword(Exception):
    pass


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


class auth(PyLucidBasePlugin):
    def login(self):
        if DEBUG:
            self.page_msg.red(
                "Warning: DEBUG is ON! Should realy only use for debugging!"
            )

        # This view is available for anonymous users. Only a anonymous user
        # must login ;)
        # But the html line <meta name="robots" content="{{ robots }}" />
        # should be set to "NONE,NOARCHIVE"
        self.request.anonymous_view = False

        UsernameForm = forms.form_for_model(User, fields=("username",))

        next_url = self.request.GET.get("next", "")

        def get_data(form):
            if DEBUG: self.page_msg(self.request.POST)

            if not form.is_valid():
                self.page_msg.red("Form data is not valid. Please correct.")
                if DEBUG: self.page_msg(form.errors)
                return

            username = form.cleaned_data["username"]
            try:
                user = User.objects.get(username = username)
            except User.DoesNotExist, e:
                msg = _("User does not exist.")
                if DEBUG: msg += " %s" % e
                self.page_msg.red(msg)
                return

            if not user.is_active:
                self.page_msg.red(_("Error: Your account is disabled!"))
                return

            return user

        if self.request.method != 'POST':
            username_form = UsernameForm()
        else:
            username_form = UsernameForm(self.request.POST)
            user = get_data(username_form)
            if user != None: # A valid form with a existing user was send.
                if not user.has_usable_password():
                    msg = _("No usable password was saved.")
                    # Display the pass reset form
                    self.pass_reset(user.username, msg)
                    return

                if "plaintext_login" in self.request.POST:
                    return self._plaintext_login(user)
                elif "sha_login" in self.request.POST:
                    return self._sha_login(user)
                else:
                    self.page_msg.red("Wrong POST data.")

        if DEBUG: self.page_msg("Next URL: %s" % next_url)

        context = {
            "fallback_url": self.URLs.adminLink(""),
            "form": username_form,
            "next_url": next_url,
        }
        self._render_template("input_username", context)#, debug=True)

    def _insert_reset_link(self, context):
        """
        insert the link to the method self.pass_reset()
        used in self._plaintext_login() and self._sha_login()
        """
        context["pass_reset_link"] = self.URLs.methodLink("pass_reset")

    def _plaintext_login(self, user):

        PasswordForm = forms.form_for_model(User, fields=("password",))

        next_url = self.request.POST.get('next_url', "")

        # Change the default TextInput to a PasswordInput
        PasswordForm.base_fields['password'].widget = forms.PasswordInput()

        context = {
            "username": user.username,
            "logout_url": self.URLs.methodLink("logout"),
            "next_url": next_url,
        }

        # Delete the default django help text:
        PasswordForm.base_fields['password'].help_text = ""

        if "password" in self.request.POST:
            password_form = PasswordForm(self.request.POST)
            if password_form.is_valid():
                password = password_form.cleaned_data["password"]
                try:
                    return self._check_plaintext_password(password, user)
                except WrongPassword, msg:
                    self.page_msg.red(msg)
                    self._insert_reset_link(context)
        else:
            password_form = PasswordForm()

        context["form"] = password_form
        self._render_template("plaintext_login", context)#, debug=True)

    def _check_plaintext_password(self, input_pass, user):
        db_pass = user.password
        if DEBUG:
            self.page_msg("password:", input_pass, db_pass)

        user = authenticate(username=user.username, password=input_pass)

        if user == None:
            raise WrongPassword("Wrong password.")

        return self._login_user(user)


    def _login_user(self, user):
        """
        Log the >user< in.
        Used in self._check_plaintext_password() and self._sha_login()
        Returns a redirect, if "next_url" exists otherwise returns None (for
        display the current page).
        """
        self.page_msg.green(_("Password ok."))
        login(self.request, user)

        # rebuild the login/logout link:
        add_dynamic_context(self.request, self.context)

        if self.request.POST.get("next_url","") != "":
            next_url = self.request.POST['next_url']

            # Redirect to next URL
            return HttpResponseRedirect(next_url)


    def _sha_login(self, user):
        """
        Login with the JS-SHA1-Login procedure.
        """
        try:
            js_login_data = JS_LoginData.objects.get(user = user)
        except JS_LoginData.DoesNotExist, e:
            msg = _(
                "The JS-SHA-Login data doesn't exist."
            )
            if DEBUG:
                msg += " %s" % e
            self.pass_reset(user.username, msg) # Display the pass reset form
            return
        next_url = self.request.POST.get('next_url',self.URLs['scriptRoot'])
        salt = js_login_data.salt

        media_url = posixpath.join(
            settings.MEDIA_URL, settings.PYLUCID_MEDIA_DIR,
        )
        context = {
            "username": user.username,
            "fallback_url": self.URLs.adminLink(""),
            "salt": salt,
            "next_url": next_url,
            "PyLucid_media_url": media_url,
        }

        if "sha_a2" in self.request.POST and "sha_b" in self.request.POST:
            SHA_login_form = SHA_LoginForm(self.request.POST)
            if not SHA_login_form.is_valid():
                self.page_msg.red("Form data is not valid. Please correct.")
                if DEBUG: self.page_msg(SHA_login_form.errors)
            else:
                sha_a2 = SHA_login_form.cleaned_data["sha_a2"]
                sha_b = SHA_login_form.cleaned_data["sha_b"]
                if DEBUG:
                    self.page_msg("sha_a2:", sha_a2)
                    self.page_msg("sha_b:", sha_b)

                # A submited SHA1-JS-Login form
                try:
                    challenge = self.request.session['challenge']
                    if DEBUG: self.page_msg("challenge:", challenge)
                except KeyError, e:
                    msg = _("Session Error.")
                    if DEBUG: msg = "%s (%s)" % (msg, e)
                    self.page_msg.red(msg)
                    return

                sha_checksum = js_login_data.sha_checksum
                if DEBUG: self.page_msg("sha_checksum:", sha_checksum)

                # authenticate with:
                # PyLucid.plugins_internal.auth.auth_backend.JS_SHA_Backend
                msg = _("Wrong password.")
                try:
                    user = authenticate(
                        user=user, challenge=challenge,
                        sha_a2=sha_a2, sha_b=sha_b,
                        sha_checksum=sha_checksum
                    )
                except Exception, e:
                    if DEBUG:
                        msg += " (%s) - " % e
                        import sys, traceback
                        msg += traceback.format_exc()
                else:
                    if user:
                        return self._login_user(user)

                self._insert_reset_link(context)
                self.page_msg.red(msg)


        if DEBUG:
            challenge = "debug"
        else:
            # Create a new random salt value for the password challenge:
            challenge = crypt.get_new_salt()

        # For later checking
        self.request.session['challenge'] = challenge

        PasswordForm = forms.form_for_model(User, fields=("password",))
        password_form = PasswordForm()

        context["form"] = password_form
        context["challenge"] = challenge

        if DEBUG == True:
            # For JavaScript debug
            context["debug"] = "true"
        else:
            context["debug"] = "false"

        self._render_template("input_password", context)#, debug=True)


    def logout(self):
        logout(self.request)

        # rebuild the login/logout link:
        add_dynamic_context(self.request, self.context)

        self.page_msg.green("You logged out.")

        if not self.current_page.permitViewPublic:
            # The current page, can't see anonymous users -> reriect to the
            # default page
            default_page = get_default_page(self.request)
            url = default_page.get_absolute_url()
            return HttpResponseRedirect(url)

    #__________________________________________________________________________
    # Password reset

    def pass_reset(self, username=None, msg=None):
        """
        Input username and email for a password reset.
        """
        if msg:
            # Plaintext or SHA1 Login and the user has a unuseable password.
            self.page_msg.red(msg)
            self.page_msg.green(_("You must reset your password."))

        ResetForm = forms.form_for_model(User, fields=("username", "email"))

        def get_data(form):
            if not form.is_valid():
                self.page_msg.red("Form data is not valid. Please correct.")
                if DEBUG: self.page_msg(reset_form.errors)
                return

            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]

            try:
                user = User.objects.get(username = username)
            except User.DoesNotExist, e:
                msg = _("User does not exist.")
                if DEBUG: msg += " %s" % e
                self.page_msg.red(msg)
                return

            if not "@" in user.email:
                self.page_msg.red(
                    _("Can't reset password. User has no email address.")
                )
                return

            if not email == user.email:
                self.page_msg.red(
                    _("Wrong email address. Please correct.")
                )
                return

            return user


        if self.request.method == 'POST' and username==None:
            if DEBUG: self.page_msg(self.request.POST)

            reset_form = ResetForm(self.request.POST)

            user = get_data(reset_form)
            if user != None: # A valid form was sended in the past
                self._send_reset_mail(user)
                return
        else:
            reset_form = ResetForm()


        context = {
            "submited": False,
            "url": self.URLs.methodLink("pass_reset"),
            "form": reset_form,
        }
        self._render_template("pass_reset_form", context)#, debug=True)


    def _send_reset_mail(self, user):
        """
        Send a mail to the user with a password reset link.
        """
        seed = crypt.get_new_seed()
        self.request.session['pass_reset_ID'] = seed

        now = datetime.datetime.now()
        expiry_time = settings.SESSION_COOKIE_AGE
        cookie_age = datetime.timedelta(seconds=expiry_time)
        expiry_date = now + cookie_age

        reset_link = self.URLs.methodLink("new_password", args=(seed,))
        reset_link = self.URLs.make_absolute_url(reset_link)

        # FIXME: convert to users local time.
        now = datetime.datetime.now()

        email_context = {
            "request_time": now,
            "base_url": self.URLs["hostname"],
            "reset_link": reset_link,
            "expiry_date": expiry_date,
            "ip": self.request.META.get('REMOTE_ADDR', "unknown") # unittest!
        }
        emailtext = self._get_rendered_template(
            "pass_reset_email", email_context,
#            debug=True
        )

        if DEBUG:
            self.page_msg("Debug! No Email was sended!")
            self.response.write("<fieldset><legend>The email text:</legend>")
            self.response.write("<pre>")
            self.response.write(emailtext)
            self.response.write("</pre></fieldset>")
        else:
            # TODO: current_domain = Site.objects.get_current().domain
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = user.email

            try:
                mail.send_mail(
                    'Password reset.', emailtext, from_email,
                    [to_email], fail_silently=False
                )
            except Exception, e:
                self.page_msg.red("Error, can't send mail: %s" % e)
                return

        context = {
            "submited": True,
            "expiry_date": expiry_date,
            "expiry_time": expiry_time,
            "expire_at_browser_close": settings.SESSION_EXPIRE_AT_BROWSER_CLOSE,
        }
        self._render_template("pass_reset_form", context)#, debug=True)


    def new_password(self, client_reset_ID = None):
        """
        view to set a new password.
        """
        if client_reset_ID == None:
            self.page_msg.red(_("Request Error!"))
            return
        if not "pass_reset_ID" in self.request.session:
            self.page_msg.red(
                _("Session expired! Set a new password it is not possible.")
            )
            self.page_msg.green(_("Please start a new password reset mail:"))
            return self.pass_reset()

        client_reset_ID = client_reset_ID.strip("/")
        pass_reset_ID = self.request.session['pass_reset_ID']
        if client_reset_ID != pass_reset_ID:
            self.page_msg.red(
                _("Wrong ID! Set a new password it is not possible.")
            )
            if DEBUG:
                self.page_msg("%s != %s" % (client_reset_ID, pass_reset_ID))
            return self.pass_reset()

        def get_data(form):
            if not form.is_valid():
                self.page_msg.red("Form data is not valid. Please correct.")
                if DEBUG: self.page_msg(form.errors)
                return

            sha_1 = form.cleaned_data["sha_1"]
            sha_2 = form.cleaned_data["sha_2"]

            return (sha_1, sha_2)

        if self.request.method == 'POST':
            if DEBUG: self.page_msg(self.request.POST)
            new_pass_form = NewPasswordForm(self.request.POST)

            sha_values = get_data(new_pass_form)
            if sha_values != None:
                sha_1, sha_2 = sha_values
                username = new_pass_form.cleaned_data["username"]

                try:
                    user = User.objects.get(username = username)
                except User.DoesNotExist, e:
                    self.page_msg.red(_("Wrong Username!"))
                    if DEBUG:
                        self.page_msg("Username:", username)
                        self.page_msg(e)
                    return

                # Set the django user account password:
                django_password = "sha1$%s$%s" % (
                    self.request.session["salt_1"], sha_1
                )
                user.password = (django_password)
                user.save()

                # Set the PyLucid password:
                login_data, status = JS_LoginData.objects.get_or_create(
                    user = user
                )
                login_data.sha_checksum = crypt.make_sha_checksum(sha_2)
                login_data.salt = self.request.session["salt_2"]
                login_data.save()

                self.page_msg.green(_("New password saved."))
                del(self.request.session['pass_reset_ID'])

                return
        else:
            new_pass_form = NewPasswordForm()

        salt_1 = crypt.get_new_salt()
        salt_2 = crypt.get_new_salt()
        self.request.session["salt_1"] = salt_1
        self.request.session["salt_2"] = salt_2

        media_url = posixpath.join(
            settings.MEDIA_URL, settings.PYLUCID_MEDIA_DIR,
        )
        context = {
            "form": new_pass_form,
            "salt_1": salt_1,
            "salt_2": salt_2,
            "PyLucid_media_url": media_url,
        }
        if DEBUG == True:
            # For JavaScript debug
            context["debug"] = "true"
        else:
            context["debug"] = "false"

        self._render_template("new_password_form", context)#, debug=True)




