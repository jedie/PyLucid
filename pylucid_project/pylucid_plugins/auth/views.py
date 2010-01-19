# coding: utf-8

"""
    PyLucid JS-SHA-Login
    ~~~~~~~~~~~~~~~~~~~~
    
    A secure JavaScript SHA-1 Login and a plaintext fallback login.
    
    Last commit info:
    ~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $
    
    :copyleft: 2007-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django.contrib import auth
from django.conf import settings
from django.template import RequestContext
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist


from pylucid.shortcuts import render_pylucid_response
from pylucid.models import LogEntry, BanEntry, UserProfile

from pylucid_project.utils import crypt

from pylucid_plugins.auth.forms import UsernameForm, PasswordForm, SHA_LoginForm
from pylucid_plugins.auth.preference_forms import AuthPreferencesForm


# DEBUG is usefull for debugging password reset. It send no email, it puts the
# email text direclty into the CMS page.
#DEBUG = True
DEBUG = False
# IMPORTANT:
# Should realy only use for debugging!!!
if DEBUG:
    import warnings
    warnings.warn("Debug mode in auth plugin is on!", UserWarning)


# For the tag list from page_admin plugin:
LUCIDTAG_EXAMPLE = """{% lucidTag admin_menu %}"""


def lucidTag(request):
    """
    Create login/logout link
    example: {% lucidTag auth %}
    """
    if request.user.is_authenticated():
        # admin_logout reverse is still broken in django, see:
        # http://code.djangoproject.com/ticket/11080
        # http://code.djangoproject.com/attachment/ticket/10061
        #url = reverse("admin:logout")
        #url = reverse("admin:index") + "logout/" # TODO: Update this if django is bugfixed
        template_name = "auth/logout_link.html"
        url = "?auth=logout"
    else:
        template_name = "auth/login_link.html"
        url = "?auth=login"

    return render_to_string(template_name, {"url": url}, context_instance=RequestContext(request))




def _logout_view(request, next_url):
    """ Logout the current user. """
    auth.logout(request)
    request.page_msg.successful(_("You are logged out!"))
    return HttpResponseRedirect(next_url)


def _login(request, user, next_url):
    last_login = user.last_login

    auth.login(request, user)

    message = render_to_string('auth/login_info.html', {"last_login":last_login})
    request.page_msg.successful(message)

    return HttpResponseRedirect(next_url)


def _plaintext_login(request, context, username, next_url):
    """ input the password and login if auth ok """
    if "password" in request.POST:
        password_form = PasswordForm(request.POST)
        if password_form.is_valid(username):
            user = password_form.user # User instance added in UsernameForm.is_valid()
            return _login(request, user, next_url)
    else:
        password_form = PasswordForm()

    context["form"] = password_form

    # return a string for replacing the normal cms page content
    return render_pylucid_response(request, 'auth/plaintext_login.html', context)



def _sha_login(request, context, user, next_url):
    """
    Login via JS-SHA-Login.
    Display the JS-SHA-Login form and login if password is ok.
    """
    try:
        user_profile = user.get_profile()
    except UserProfile.DoesNotExist, err:
        try:
            UserProfile.objects.get(user=user)#.count()
        except UserProfile.DoesNotExist, err:
            # User profile doesn't generally not exist for this user. e.g. Update from v0.8.x ?
            msg = _("There exist no UserProfile for user %(user)r: %(err)s") % {"user":user, "err":err}
        else:
            # A UserProfile exist -> User can't access *this* site.
            site = Site.objects.get_current()
            msg = _("User %(user)r can't access this site: %(site)r") % {"user":user, "site": site}

        LogEntry.objects.log_action(
            app_label="pylucid_plugin.auth", action="login", message=msg
        )

        if settings.DEBUG:
            request.page_msg.error(msg)
        else:
            request.page_msg.error(_("User unknown."))

        return

    if "sha_a2" in request.POST and "sha_b" in request.POST:
        SHA_login_form = SHA_LoginForm(request.POST)
        if not SHA_login_form.is_valid():
            msg = _("Form data is not valid. Please correct.")
            request.page_msg.error(msg)
            LogEntry.objects.log_action(
                app_label="pylucid_plugin.auth", action="login",
                message="%s (%r)" % (msg, SHA_login_form.errors)
            )
            if DEBUG: request.page_msg(SHA_login_form.errors)
        else:
            sha_a2 = SHA_login_form.cleaned_data["sha_a2"]
            sha_b = SHA_login_form.cleaned_data["sha_b"]
            if DEBUG:
                request.page_msg("sha_a2:", sha_a2)
                request.page_msg("sha_b:", sha_b)

            # A submited SHA1-JS-Login form
            try:
                challenge = request.session['challenge']
                if DEBUG: request.page_msg("challenge:", challenge)
            except KeyError, e:
                msg = _("Session Error.")
                LogEntry.objects.log_action(
                    app_label="pylucid_plugin.auth", action="login", message=msg,
                    data={"user_username": user.username}
                )
                if DEBUG: msg = "%s (%s)" % (msg, e)
                request.page_msg.error(msg)
                return

            sha_checksum = user_profile.sha_login_checksum
            if DEBUG: request.page_msg("sha_checksum:", sha_checksum)

            # authenticate with:
            # pylucid.system.auth_backends.SiteSHALoginAuthBackend
            user2 = auth.authenticate(
                user=user, challenge=challenge,
                sha_a2=sha_a2, sha_b=sha_b,
                sha_checksum=sha_checksum
            )
            if user2:
                return _login(request, user2, next_url)

            msg = _("Wrong password.")
            LogEntry.objects.log_action(
                app_label="pylucid_plugin.auth", action="login", message=msg,
                data={"user_username": user.username}
            )
            request.page_msg.error(msg)
    else:
        SHA_login_form = UsernameForm()


    context["salt"] = user_profile.sha_login_salt
    if DEBUG:
        challenge = "debug" # Use same challenge in debug mode
        context["debug"] = "true" # For JavaScript debug
    else:
        # Create a new random salt value for the password challenge:
        challenge = crypt.get_new_salt()
        context["debug"] = "false"

    # For later comparing with form data
    request.session['challenge'] = challenge
    context["challenge"] = challenge

    context["form"] = SHA_login_form

    # return a string for replacing the normal cms page content
    return render_pylucid_response(request, 'auth/input_password.html', context,
        context_instance=RequestContext(request)
    )


def _login_view(request, form_url, next_url):
    if DEBUG:
        request.page_msg(
            "Warning: DEBUG is ON! Should realy only use for debugging!"
        )

    pref_form = AuthPreferencesForm()
    preferences = pref_form.get_preferences()
    min_pause = preferences["min_pause"]
    ban_limit = preferences["ban_limit"]

    try:
        LogEntry.objects.request_limit(request, min_pause, ban_limit, app_label="pylucid_plugin.auth")
    except LogEntry.RequestTooFast:
        # min_pause is not observed, page_msg has been created -> display the normal cms page.
        return

    context = request.PYLUCID.context
    context["form_url"] = form_url

    if request.method == 'POST':
        username_form = UsernameForm(request.POST)
        if username_form.is_valid():
            user = username_form.user # User instance added in UsernameForm.is_valid()
            if not user.is_active:
                msg = _("Error: Your account is disabled!")
                LogEntry.objects.log_action(
                    app_label="pylucid_plugin.auth", action="login", message=msg,
                    data={"user_username": user.username}
                )
                request.page_msg.error(msg)
                return

            context["username"] = user.username

            if "plaintext_login" in request.POST:
                return _plaintext_login(request, context, user.username, next_url)
            else:
                return _sha_login(request, context, user, next_url)
    else:
        username_form = UsernameForm()

    context["form"] = username_form

    # return a string for replacing the normal cms page content
    return render_pylucid_response(request, 'auth/input_username.html', context)


def http_get_view(request):
    """
    Login+Logout view via GET parameters
    """
    action = request.GET["auth"]
    if action == "login":
        next_url = request.GET.get("next_url", None)
        if next_url:
            form_url = settings.PYLUCID.AUTH_NEXT_URL % {"path": request.path, "next_url": next_url}
        else:
            next_url = request.path
            form_url = "%s?%s" % (request.path, settings.PYLUCID.AUTH_GET_VIEW)

        return _login_view(request, form_url, next_url)
    elif action == "logout":
        next_url = request.path
        return _logout_view(request, next_url)

    msg = _("Wrong get view parameter!")
    LogEntry.objects.log_action(app_label="pylucid_plugin.auth", action="login", message=msg)
    if settings.DEBUG:
        request.page_msg.error(msg)


def authenticate(request):
    """
    Login+Logout view via PluginPage
    """
    if request.user.is_authenticated():
        return _logout_view(request)
    else:
        next_url = request.GET.get("next_url", None)
        form_url = request.path
        if next_url == None:
            next_url = "/"
        else:
            form_url += "?next_url=" + next_url

        return _login_view(request, form_url, next_url)

