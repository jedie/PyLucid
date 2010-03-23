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
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string

from pylucid_project.apps.pylucid.shortcuts import render_pylucid_response
from pylucid_project.apps.pylucid.models import LogEntry
from pylucid_project.utils import crypt

# auth own stuff
from forms import WrongUserError, UsernameForm, ShaLoginForm
from preference_forms import AuthPreferencesForm


# DEBUG is usefull for debugging. It send always the same challenge "12345" 
#DEBUG = True
DEBUG = False
# IMPORTANT: Should really only use for debugging!!!
if DEBUG:
    import warnings
    warnings.warn("Debug mode in auth plugin is on! print statements would be used!")


def _get_challenge(request):
    """ create a new challenge, add it to session and return it"""
    if DEBUG:
        challenge = "12345"
        print("use DEBUG challenge: %r" % challenge)
    else:
        # Create a new random salt value for the password challenge:
        challenge = crypt.get_new_salt()

    # For later comparing with form data
    request.session["challenge"] = challenge

    return challenge


def _bad_request(debug_msg):
    """
    Create a new LogEntry and return a HttpResponseBadRequest
    """
    LogEntry.objects.log_action(
        app_label="pylucid_plugin.auth", action="login error", message=debug_msg,
    )
    if settings.DEBUG:
        msg = debug_msg
    else:
        msg = ""

    return HttpResponseBadRequest(msg)


def _is_post_ajax_request(request):
    if not request.is_ajax():
        debug_msg = "request is not a ajax request"
        return _bad_request(debug_msg)

    if request.method != 'POST':
        debug_msg = "request method %r wrong, only POST allowed" % request.method
        return _bad_request(debug_msg)


def lucidTag(request):
    """
    Create login/logout link
    example: {% lucidTag auth %}
    """
    if request.user.is_authenticated():
        template_name = "auth/logout_link.html"
        if hasattr(request.PYLUCID, "pagetree"):
            # We are on a normal cms page -> Dont's change the url
            url = ""
        else:
            # We are in the django admin panel -> Go to root page
            url = "/"
        url += "?auth=logout"
    else:
        template_name = "auth/login_link.html"
        url = "?auth=login"

    return render_to_string(template_name, {"url": url}, context_instance=RequestContext(request))


def _wrong_login(request, debug_msg, user=None):
    """ username or password is wrong. """
    if settings.DEBUG:
        error_msg = debug_msg
    else:
        error_msg = _("Wrong username/password.")

    # Protection against DOS attacks.
    pref_form = AuthPreferencesForm()
    preferences = pref_form.get_preferences()
    min_pause = preferences["min_pause"]
    ban_limit = preferences["ban_limit"]
    try:
        LogEntry.objects.request_limit(
            request, min_pause, ban_limit, app_label="pylucid_plugin.auth", no_page_msg=True
        )
    except LogEntry.RequestTooFast, err:
        # min_pause is not observed
        error_msg = unicode(err) # ugettext_lazy

    # Log this error (Important: must be logged after LogEntry.objects.request_limit() stuff!
    if user is not None:
        data = {"user_username": user.username}
    else:
        data = None
    LogEntry.objects.log_action(
        app_label="pylucid_plugin.auth", action="login", message=debug_msg, data=data
    )

    # create a new challenge and add it to session
    challenge = _get_challenge(request)

    response = "%s;%s" % (challenge, error_msg)
    return HttpResponse(response, content_type="text/plain")


def _sha_auth(request):
    """
    login the user with username and sha values.
    """
    response = _is_post_ajax_request(request)
    if response is not None: # It's not a Ajax POST request
        return response # Return HttpResponseBadRequest

    form = ShaLoginForm(request.POST)
    if not form.is_valid():
        debug_msg = "ShaLoginForm is not valid: %r" % form.errors
        return _bad_request(debug_msg)

    try:
        challenge = request.session.pop("challenge")
    except KeyError, err:
        debug_msg = "Can't get 'challenge' from session: %s" % err
        return _bad_request(debug_msg)

    try:
        user1, user_profile = form.get_user_and_profile()
    except WrongUserError, err:
        debug_msg = "Can't get user and user profile: %s" % err
        return _wrong_login(request, debug_msg)

    sha_checksum = user_profile.sha_login_checksum
    sha_a2 = form.cleaned_data["sha_a2"]
    sha_b = form.cleaned_data["sha_b"]

    if DEBUG:
        print(
            "authenticate %r with: challenge: %r, sha_checksum: %r, sha_a2: %r, sha_b: %r" % (
                user1, challenge, sha_checksum, sha_a2, sha_b
            )
        )

    try:
        # authenticate with:
        # pylucid.system.auth_backends.SiteSHALoginAuthBackend
        user2 = auth.authenticate(
            user=user1, challenge=challenge,
            sha_a2=sha_a2, sha_b=sha_b,
            sha_checksum=sha_checksum
        )
    except Exception, err: # e.g. low level error from crypt
        debug_msg = "auth.authenticate() failed: %s" % err
        return _wrong_login(request, debug_msg, user1)

    if user2 is None:
        debug_msg = "auth.authenticate() failed. (must be a wrong password)"
        return _wrong_login(request, debug_msg, user1)
    else:
        # everything is ok -> log the user in and display "last login" page message
        last_login = user2.last_login
        auth.login(request, user2)
        message = render_to_string('auth/login_info.html', {"last_login":last_login})
        request.page_msg.successful(message)
        return HttpResponse("OK", content_type="text/plain")


def _get_salt(request):
    """
    return the user password salt.
    If the user doesn't exist or is not active, return a pseudo salt.
    """
    response = _is_post_ajax_request(request)
    if response is not None: # It's not a Ajax POST request
        return response # Return HttpResponseBadRequest

    user_profile = None
    form = UsernameForm(request.POST)
    if form.is_valid():
        try:
            user_profile = form.get_user_profile()
        except WrongUserError, err:
            msg = "can't get userprofile: %s" % err
            if DEBUG:
                print(msg)
            if settings.DEBUG:
                request.page_msg.error(msg)

    if user_profile is None: # Wrong user?
        username = request.POST["username"]
        msg = "Username %r is wrong: %r" % (username, form.errors)
        if DEBUG:
            print(msg)
        if settings.DEBUG:
            request.page_msg.error(msg)
        salt = crypt.get_pseudo_salt(username)
    else:
        salt = user_profile.sha_login_salt
        if len(salt) != crypt.SALT_LEN:
            # Old profile, e.g. after PyLucid v0.8 update?
            username = request.POST["username"]
            msg = "Salt for user %r has wrong length: %r" % (username, salt)
            if DEBUG:
                print(msg)
            if settings.DEBUG:
                request.page_msg.error(msg)
            salt = crypt.get_pseudo_salt(username)

    if DEBUG:
        print("send salt %r to client." % salt)

    return HttpResponse(salt, content_type="text/plain")


def _login_view(request):
    if DEBUG:
        print("auth debug mode is on!")

    if request.method != 'GET':
        debug_msg = "request method %r wrong, only GET allowed" % request.method
        return _bad_request(debug_msg) # Return HttpResponseBadRequest

    next_url = request.GET.get("next_url", request.path)

    if "://" in next_url: # FIXME: How to validate this better?
        # Don't redirect to other pages.
        debug_msg = "next url %r seems to be wrong!" % next_url
        return _bad_request(debug_msg) # Return HttpResponseBadRequest

    form = ShaLoginForm()

    # create a new challenge and add it to session
    challenge = _get_challenge(request)

    context = {
        "is_ajax": request.is_ajax(),
        "challenge": challenge,
        "salt_len": crypt.SALT_LEN,
        "hash_len": crypt.HASH_LEN,
        "get_salt_url": request.path + "?auth=get_salt",
        "sha_auth_url": request.path + "?auth=sha_auth",
        "next_url": next_url,
        "form": form,
        "pass_reset_link": "#TODO",
    }

    # return a string for replacing the normal cms page content
    return render_pylucid_response(request, 'auth/sha_form.html', context, context_instance=RequestContext(request))


def _logout_view(request):
    """ Logout the current user. """
    auth.logout(request)
    request.page_msg.successful(_("You are logged out!"))
    next_url = request.path
    return HttpResponseRedirect(next_url)


def http_get_view(request):
    """
    Login+Logout view via GET parameters
    """
    action = request.GET["auth"]

    if action == "login":
        return _login_view(request)
    elif action == "get_salt":
        return _get_salt(request)
    elif action == "sha_auth":
        return _sha_auth(request)
    elif action == "logout":
        return _logout_view(request)
    else:
        debug_msg = "Wrong get view parameter!"
        return _bad_request(debug_msg) # Return HttpResponseBadRequest


