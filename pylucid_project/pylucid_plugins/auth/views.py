# coding:utf-8

from django.contrib import auth
from django.conf import settings
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from pylucid_project.utils import crypt

from auth.forms import UsernameForm, PasswordForm, SHA_LoginForm


# DEBUG is usefull for debugging password reset. It send no email, it puts the
# email text direclty into the CMS page.
#DEBUG = True
DEBUG = False
# IMPORTANT:
# Should realy only use for debugging!!!
if DEBUG:
    import warnings
    warnings.warn("Debug mode in auth plugin is on!", UserWarning)


def _logout_view(request):
    """ Logout the current user. """
    auth.logout(request)
    request.page_msg.successful(_("You are logged out!"))


def _login(request, user, next_url):
    auth.login(request, user)
    request.page_msg.successful(_("You are logged in!"))
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
    return render_to_string('auth/plaintext_login.html', context)


    
def _sha_login(request, context, user, next_url):
    """
    Login via JS-SHA-Login.
    Display the JS-SHA-Login form and login if password is ok.
    """
    user_profile = user.get_profile()
    
    if "sha_a2" in request.POST and "sha_b" in request.POST:
        SHA_login_form = SHA_LoginForm(request.POST)
        if not SHA_login_form.is_valid():
            request.page_msg.error(_("Form data is not valid. Please correct."))
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
                if DEBUG: msg = "%s (%s)" % (msg, e)
                request.page_msg.error(msg)
                return

            sha_checksum = user_profile.sha_login_checksum
            if DEBUG: request.page_msg("sha_checksum:", sha_checksum)

            # authenticate with:
            # pylucid.system.auth_backends.SiteSHALoginAuthBackend
            user = auth.authenticate(
                user=user, challenge=challenge,
                sha_a2=sha_a2, sha_b=sha_b,
                sha_checksum=sha_checksum
            )
            if user:
                return _login(request, user, next_url)
            request.page_msg.error(_("Wrong password."))                    
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
    return render_to_string('auth/input_password.html', context)


def _login_view(request, form_url, next_url):
    if DEBUG:
        request.page_msg(
            "Warning: DEBUG is ON! Should realy only use for debugging!"
        )
    
    context = request.PYLUCID.context
    context["form_url"] = form_url

    if request.method == 'POST':
        username_form = UsernameForm(request.POST)
        if username_form.is_valid():
            user = username_form.user # User instance added in UsernameForm.is_valid()
            if not user.is_active:
                request.page_msg.error("Error: Your account is disabled!")
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
    return render_to_string('auth/input_username.html', context)


def http_get_view(request):
    """
    Login+Logout view via GET parameters
    """
    action = request.GET["auth"]
    if action=="login":
        form_url = request.path + "?auth=login" # FIXME: How can we add the GET Parameter?
        next_url = request.path
        return _login_view(request, form_url, next_url)
    elif action=="logout":
        return _logout_view(request)
    
    if settings.DEBUG:
        request.page_msg(_("Wrong get view parameter!"))


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

