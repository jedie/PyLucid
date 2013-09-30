# coding: utf-8


"""
    PyLucid JS-SHA-Login
    ~~~~~~~~~~~~~~~~~~~~

    secure JavaScript SHA-1 AJAX Login
    more info:
        http://www.pylucid.org/permalink/42/secure-login-without-https

    :copyleft: 2007-2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""


from django.conf import settings
from django.contrib import auth, messages
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from django.core import urlresolvers
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from pylucid_project.apps.pylucid.decorators import check_request
from pylucid_project.apps.pylucid.models import LogEntry
from pylucid_project.apps.pylucid.models.pluginpage import PluginPage
from pylucid_project.apps.pylucid.shortcuts import bad_request, ajax_response
from pylucid_project.pylucid_plugins.auth.forms import HoneypotForm
from pylucid_project.pylucid_plugins.auth.models import HonypotAuth, \
    CNONCE_CACHE
from pylucid_project.utils import crypt

# auth own stuff
from forms import WrongUserError, UsernameForm, ShaLoginForm
from preference_forms import AuthPreferencesForm


APP_LABEL = "pylucid_plugin.auth" # used for creating LogEntry entries


# DEBUG is usefull for debugging. It send always the same challenge "12345"
# DEBUG = True
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
        challenge = crypt.get_new_seed()

    # For later comparing with form data
    request.session["challenge"] = challenge

    return challenge

def _get_loop_count():
    pref_form = AuthPreferencesForm()
    preferences = pref_form.get_preferences()
    loop_count = preferences["loop_count"]
    return loop_count


@csrf_exempt
def login_honeypot(request):
    """
    A login honypot.
    """
    faked_login_error = False
    if request.method == 'POST':
        form = HoneypotForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            HonypotAuth.objects.add(request, username, password)
            messages.error(request, _("username/password wrong."))
            form = HoneypotForm(initial={"username": username})
            faked_login_error = True
    else:
        form = HoneypotForm()
    context = {
        "form": form,
        "form_url": request.path,
        "page_robots": "noindex,nofollow",
    }

    response = render_to_response("auth/login_honeypot.html", context, context_instance=RequestContext(request))
    if faked_login_error:
        response.status_code = 401
    return response


def lucidTag(request):
    """
    Create login/logout link
    example: {% lucidTag auth %}
    """
    context = {
        "honypot_url": "#top" # Don't use honypot
    }
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
        pref_form = AuthPreferencesForm()
        preferences = pref_form.get_preferences()
        use_honypot = preferences["use_honypot"]
        if use_honypot:
            try: # Use the first PluginPage instance
                honypot_url = PluginPage.objects.reverse("auth", 'Auth-login_honeypot')
            except urlresolvers.NoReverseMatch, err:
                if settings.RUN_WITH_DEV_SERVER:
                    print "*** Can't get 'Auth-login_honeypot' url: %s" % err
            else:
                context["honypot_url"] = honypot_url

        https_urls = preferences["https_urls"]
        if not https_urls:
            template_name = "auth/login_link.html"
            url = ""
        else:
            # Use https for login
            template_name = "auth/login_link_https.html"
            url = "https://%s%s" % (request.get_host(), request.path)

        url += "?auth=login"

    context["url"] = url

    return render_to_string(template_name, context, context_instance=RequestContext(request))


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
            request, min_pause, ban_limit, app_label="pylucid_plugin.auth", action="login error", no_page_msg=True
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
        app_label="pylucid_plugin.auth", action="login error", message=debug_msg, data=data
    )

    # create a new challenge and add it to session
    challenge = _get_challenge(request)

    response = "%s;%s" % (challenge, error_msg)
    return HttpResponse(response, content_type="text/plain")



@check_request(app_label="pylucid_plugin.auth", action="_sha_auth() error", must_post=True, must_ajax=True)
@csrf_protect
def _sha_auth(request):
    """
    login the user with username and sha values.
    """
    _NORMAL_ERROR_MSG = "_sha_auth() error"

    form = ShaLoginForm(request.POST)
    if not form.is_valid():
        debug_msg = "ShaLoginForm is not valid: %s" % repr(form.errors)
        return bad_request(APP_LABEL, _NORMAL_ERROR_MSG, debug_msg)

    try:
        challenge = request.session.pop("challenge")
    except KeyError, err:
        debug_msg = "Can't get 'challenge' from session: %s" % err
        return bad_request(APP_LABEL, _NORMAL_ERROR_MSG, debug_msg)

    try:
        user1, user_profile = form.get_user_and_profile()
    except WrongUserError, err:
        debug_msg = "Can't get user and user profile: %s" % err
        return _wrong_login(request, debug_msg)

    loop_count = _get_loop_count() # get "loop_count" from AuthPreferencesForm

    sha_checksum = user_profile.sha_login_checksum
    sha_a = form.cleaned_data["sha_a"]
    sha_b = form.cleaned_data["sha_b"]
    cnonce = form.cleaned_data["cnonce"]

    # Simple check if 'nonce' from client used in the past.
    # Limitations:
    #  - Works only when run in a long-term server process, so not in CGI ;)
    #  - dict vary if more than one server process runs (one dict in one process)
    if cnonce in CNONCE_CACHE:
        debug_msg = "Client-nonce '%s' used in the past!" % cnonce
        return bad_request(APP_LABEL, _NORMAL_ERROR_MSG, debug_msg)
    CNONCE_CACHE[cnonce] = None

    if DEBUG:
        print(
            "authenticate %r with: challenge: %r, sha_checksum: %r, sha_a: %r, sha_b: %r, cnonce: %r" % (
                user1, challenge, sha_checksum, sha_a, sha_b, cnonce
            )
        )

    try:
        # authenticate with:
        # pylucid.system.auth_backends.SiteSHALoginAuthBackend
        user2 = auth.authenticate(
            user=user1, challenge=challenge,
            sha_a=sha_a, sha_b=sha_b,
            sha_checksum=sha_checksum,
            loop_count=loop_count, cnonce=cnonce
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
        messages.success(request, message)
        return HttpResponse("OK", content_type="text/plain")


@check_request(app_label="pylucid_plugin.auth", action="_get_salt() error", must_post=True, must_ajax=True)
@csrf_protect
def _get_salt(request):
    """
    return the user password salt.
    If the user doesn't exist or is not active, return a pseudo salt.
    """
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
                messages.error(request, msg)

    if user_profile is None: # Wrong user?
        username = request.POST["username"]
        msg = "Username %r is wrong: %r" % (username, form.errors)
        if DEBUG:
            print(msg)
        if settings.DEBUG:
            messages.error(request, msg)
        salt = crypt.get_pseudo_salt(username)
    else:
        salt = user_profile.sha_login_salt
        if len(salt) not in (crypt.SALT_LEN, crypt.OLD_SALT_LEN):
            # Old profile, e.g. after PyLucid v0.8 update?
            username = request.POST["username"]
            msg = "Salt for user %r has wrong length: %r" % (username, salt)
            if DEBUG:
                print(msg)
            if settings.DEBUG:
                messages.error(request, msg)
            salt = crypt.get_pseudo_salt(username)

    if DEBUG:
        print("send salt %r to client." % salt)

    return HttpResponse(salt, content_type="text/plain")


@csrf_protect
def _login_view(request):
    """
    For better JavaScript debugging: Enable settings.DEBUG and request the page
    via GET with: "...?auth=login"
    """
    if DEBUG:
        print("auth debug mode is on!")

    if request.method != 'GET':
        debug_msg = "request method %r wrong, only GET allowed" % request.method
        return bad_request(APP_LABEL, "_login_view() error", debug_msg) # Return HttpResponseBadRequest

    next_url = request.GET.get("next_url", request.path)

    if "//" in next_url: # FIXME: How to validate this better?
        # Don't redirect to other pages.
        debug_msg = "next url %r seems to be wrong!" % next_url
        return bad_request(APP_LABEL, "_login_view() error", debug_msg) # Return HttpResponseBadRequest

    form = ShaLoginForm()

    # create a new challenge and add it to session
    challenge = _get_challenge(request)

    try:
        # url from django-authopenid, only available if the urls.py are included
        reset_link = urlresolvers.reverse("auth_password_reset")
    except urlresolvers.NoReverseMatch:
        try:
            # DjangoBB glue plugin adds the urls from django-authopenid
            reset_link = PluginPage.objects.reverse("djangobb_plugin", "auth_password_reset")
        except KeyError:
            # plugin is not installed
            reset_link = None
        except urlresolvers.NoReverseMatch:
            # plugin is installed, but not in used (no PluginPage created)
            reset_link = None

    loop_count = _get_loop_count() # get "loop_count" from AuthPreferencesForm

    context = {
        "challenge": challenge,
        "old_salt_len": crypt.OLD_SALT_LEN,
        "salt_len": crypt.SALT_LEN,
        "hash_len": crypt.HASH_LEN,
        "loop_count": loop_count,
        "get_salt_url": request.path + "?auth=get_salt",
        "sha_auth_url": request.path + "?auth=sha_auth",
        "next_url": next_url,
        "form": form,
        "pass_reset_link": reset_link,
    }

    # IMPORTANT: We must do the following, so that the
    # CsrfViewMiddleware.process_response() would set the CSRF_COOKIE
    # see also # https://github.com/jedie/PyLucid/issues/61
    # XXX in Django => 1.4 we can use @ensure_csrf_cookie
    # https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#django.views.decorators.csrf.ensure_csrf_cookie
    request.META["CSRF_COOKIE_USED"] = True

    # return a string for replacing the normal cms page content
    if not request.is_ajax():
        response = render_to_response('auth/sha_form_debug.html', context, context_instance=RequestContext(request))
    else:
        response = ajax_response(request, 'auth/sha_form.html', context, context_instance=RequestContext(request))

    return response


def _logout_view(request):
    """ Logout the current user. """
    auth.logout(request)
    messages.success(request, _("You are logged out!"))
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
        return bad_request(APP_LABEL, "http_get_view() error", debug_msg) # Return HttpResponseBadRequest


