
"""
A base class for every _install view.
"""

import sys, os, posixpath

from PyLucid import PYLUCID_VERSION_STRING
from PyLucid.system.response import SimpleStringIO
from PyLucid.system.page_msg import PageMessages
from PyLucid.system.utils import setup_request
from PyLucid.tools import crypt
from PyLucid.tools.content_processors import render_string_template

from django.conf import settings
from django.shortcuts import render_to_response
from django import forms
from django.http import HttpResponse, Http404
from django.utils.translation import ugettext as _
from django.template import Template, Context, loader
# The loader must be import, even if it is not used directly!!!
# Note: The loader makes this: add_to_builtins('django.template.loader_tags')
# In loader_tags are 'block', 'extends' and 'include' defined.


# Warning: If debug is on, the install password is in the traceback!!!
#DEBUG = True
DEBUG = False


class WrongInstallPassHash(Exception):
    pass

def check_install_pass():
    """
    Check if the install pass hash set in the settings.py and if the length
    and type is ok.
    """
    if settings.INSTALL_PASSWORD_HASH in (None, ""):
        if DEBUG:
            msg = _("The _install section password hash is not set.")
        else:
            msg = ""
        raise WrongInstallPassHash(msg)

    current_len = len(settings.INSTALL_PASSWORD_HASH)
    if current_len != crypt.SALT_HASH_LEN:
        msg = "Wrong hash len in your settings.py!"
        if DEBUG:
            msg += " - Should be: %s current length is: %s" % (
                crypt.SALT_HASH_LEN, current_len
            )
        raise WrongInstallPassHash(msg)

    if not settings.INSTALL_PASSWORD_HASH.startswith("sha1$"):
        raise WrongInstallPassHash("Wrong hash format in your settings.py!")


def check_password_hash(password_hash):
    """
    """
    def error(msg):
        msg = _("error:") + msg
        if DEBUG:
            msg += " [Debug: '%s' != '%s']" % (
                password_hash, settings.INSTALL_PASSWORD_HASH
            )
        raise WrongPassword(msg)
    if len(password_hash) != crypt.SALT_HASH_LEN:
        error(_("Wrong password hash len."))
    if password_hash != settings.INSTALL_PASSWORD_HASH:
        error(_("Password compare fail."))



class InstallPassForm(forms.Form):
    """ a django newforms for input the _install section password """
    hash = forms.CharField(min_length=crypt.SALT_HASH_LEN, max_length=crypt.SALT_HASH_LEN)

SIMPLE_RENDER_TEMPLATE = """
{% extends "install_base.html" %}
{% block content %}
{% if headline %}<h1>{{ headline|escape }}</h1>{% endif %}
<pre>{{ output|escape }}</pre>
{% endblock %}
"""

def get_base_context(request):
    """
    Build a base context.
    Used in BaseInstall and PyLucidCommonMiddleware.
    """
    media_url = posixpath.join(
        settings.MEDIA_URL, settings.PYLUCID_MEDIA_DIR, ""
    ) # With appended slash, for backward compatible
    context = {
        "output": "",
        "request": request,
        "PyLucid_media_url": media_url,
        "version": PYLUCID_VERSION_STRING,
        "current_working_dir": os.getcwd(),
    }
    return context



class BaseInstall(object):
    """
    Base class for all install views.
    """
    def __init__(self, request):
        if not hasattr(settings, "INSTALL_PASSWORD_HASH"):
            raise WrongInstallPassHash(
                "Error:"
                " INSTALL_PASS_HASH has been renamed to INSTALL_PASSWORD_HASH!"
                " Please rename this variable in your settings.py"
                " - more information: http://www.pylucid.org/_goto/121/changes/"
            )

        if settings.ENABLE_INSTALL_SECTION != True:
            # Should never nappen, because the urlpatterns deactivaed, too.
            raise Http404("Install section disabled")

        self.page_msg = request.page_msg

        self.request = request

        self.context = get_base_context(request)

    #___________________________________________________________________________

    def __render_generate_hash(self, msg):
        """
        Display a html page for generating the password with sha1.js
        """
        # Do not display the "back to menu" link:
        self.context["no_menu_link"] = True

        if msg and msg != "": # insert the messages:
            self.request.page_msg.write(msg)

        return render_to_response(
            "install_generate_hash.html", self.context
        )

    def start_view(self, *args):
        """
        - Check the install password / login cookie
        - starts the self.view() if login ok
        - display the login form if login not ok
        """
        try:
            # Check the install hash in the settings.py
            check_install_pass()
        except WrongInstallPassHash, msg:
            return self.__render_generate_hash(msg.args[0])

        try:
            # check if the _install section password is stored in the cookie
            # and if the salt hash value is ok
            cookie_pass = self.request.COOKIES.get(settings.INSTALL_COOKIE_NAME)
            assert cookie_pass != "", "No password hash in cookie"
            crypt.check_salt_hash(settings.INSTALL_PASSWORD_HASH, cookie_pass)
        except Exception, msg:
            # Cookie is not set or the salt hash value compair failed
            if DEBUG:
                self.request.page_msg.write("DEBUG: %s" % msg)
        else:
            # access ok -> start the normal _install view() method
            return self.view(*args)

        # The _install section password is not in the cookie
        # -> display a html input form or check a submited form
        if self.request.method == 'POST':
            # A form was submit
            form = InstallPassForm(self.request.POST)
            if form.is_valid():
                # The submited form is ok
                form_data = form.cleaned_data
                password_hash = form_data["hash"]
                try:
                    check_password_hash(password_hash)
                except WrongPassword, msg:
                    # Display the form again
                    self.request.page_msg.write(msg)
                else:
                    # Password is ok. -> process the normal _instal view()
                    response = self.view(*args)
                    # insert a cookie with the hashed password in the response
                    salt_hash = crypt.make_salt_hash(str(password_hash))
                    response.set_cookie(
                        settings.INSTALL_COOKIE_NAME, value=salt_hash, max_age=None
                    )
                    return response

        data = crypt.salt_hash_to_dict(settings.INSTALL_PASSWORD_HASH)
        self.context["salt"] = data["salt"]

        self.context["no_menu_link"] = True # no "back to menu" link
#        self.request.page_msg.write(_("Please input the password"))
        return render_to_response("install_login.html", self.context)

   #___________________________________________________________________________

    def _redirect_execute(self, method, *args, **kwargs):
        """
        run a method an redirect stdout writes (print) into a Buffer.
        puts the redirected outputs into self.context["output"].
        usefull to run django management functions.
        """
        redirect = SimpleStringIO()
        old_stdout = sys.stdout
        sys.stdout = redirect
        old_stderr = sys.stderr
        sys.stderr = redirect
        try:
            try:
                method(*args, **kwargs)
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                output = redirect.getvalue()
        except Exception, e:
            # Display the written output
            # FixMe: There should be exist a better way for this.
            print output
            raise

        self.context["output"] += output

    def _render(self, template):
        """
        render the template and returns the result as a HttpResponse object.
        """
        html = render_string_template(template, self.context)
        return HttpResponse(html)

    def _simple_render(self, output=None, headline=None):
        """
        a simple way to render a output.
        Use simple_render_template.
        """
        if output:
            self.context["output"] += "".join(output)
        if headline:
            self.context["headline"] = headline
        return self._render(SIMPLE_RENDER_TEMPLATE)



class WrongPassword(Exception):
    """
    Wrong _install section password
    """
    pass






