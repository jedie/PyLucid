# coding:utf-8

from django.contrib import auth
from django.conf import settings
from django.template import RequestContext
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

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
    warnings.warn("Debugmode is on", UserWarning)

def _logout_view(request):
    auth.logout(request)
#    request.page_msg("You logged out.")
    return HttpResponseRedirect(request.path)


def _plaintext_login(request, context, username):
    """ input the password and login if auth ok """
    if "password" in request.POST:
        password_form = PasswordForm(request.POST)
        if password_form.is_valid(username):
            user = password_form.user # User instance added in UsernameForm.is_valid()
            auth.login(request, user)
            request.page_msg("You are logged in!")
            return HttpResponseRedirect(request.path)
    else:
        password_form = PasswordForm()
        
    context["form"] = password_form
    
    # return a string for replacing the normal cms page content
    return render_to_string('auth/plaintext_login.html', context)
    
    
def _sha_login(request, context, user):
    user_profile = user.get_profile()
    request.page_msg(user_profile)
    
    context["salt"] = user_profile.sha_login_salt
    if DEBUG:
        challenge = "debug"
        # For JavaScript debug
        context["debug"] = "true"
    else:
        # Create a new random salt value for the password challenge:
        challenge = crypt.get_new_salt()
        context["debug"] = "false"
    
        
    context["debug"] = "true"
    
        
    # For later comparing with form data
    request.session['challenge'] = challenge
    context["challenge"] = challenge
    
    if "sha_a2" in request.POST and "sha_b" in request.POST:
        SHA_login_form = SHA_LoginForm(request.POST)
        if not SHA_login_form.is_valid():
            request.page_msg.error("Form data is not valid. Please correct.")
            if DEBUG: request.page_msg(SHA_login_form.errors)
        else:
            sha_a2 = SHA_login_form.cleaned_data["sha_a2"]
            sha_b = SHA_login_form.cleaned_data["sha_b"]
            if DEBUG:
                request.page_msg("sha_a2:", sha_a2)
                request.page_msg("sha_b:", sha_b)
    else:
        SHA_login_form = UsernameForm()
        
    context["form"] = SHA_login_form
    
    # return a string for replacing the normal cms page content
    return render_to_string('auth/input_password.html', context)


def _login_view(request):
    if DEBUG:
        request.page_msg(
            "Warning: DEBUG is ON! Should realy only use for debugging!"
        )
    
    context = request.PYLUCID.context
    context["form_url"] = request.path + "?auth=login" # FIXME: How can we add the GET Parameter?

    if request.method == 'POST':
        request.page_msg(request.POST)
        username_form = UsernameForm(request.POST)
        if username_form.is_valid():
            user = username_form.user # User instance added in UsernameForm.is_valid()
            if not user.is_active:
                request.page_msg.error("Error: Your account is disabled!")
                return
            
            context["username"] = user.username
            
            if "plaintext_login" in request.POST:
                return _plaintext_login(request, context, user.username)
            else:
                return _sha_login(request, context, user)
    else:
        username_form = UsernameForm()
        
    context["form"] = username_form
    
    # return a string for replacing the normal cms page content
    return render_to_string('auth/input_username.html', context)

def http_get_view(request):
    """
    Login view
    """
    request.page_msg("TODO: refactor the rest from auth plugin ;)")
    
    action = request.GET["auth"]
    print action
    if action=="login":
        return _login_view(request)
    elif action=="logout":
        return _logout_view(request)
    
    if settings.DEBUG:
        request.page_msg("Wrong get view parameter!")

    
