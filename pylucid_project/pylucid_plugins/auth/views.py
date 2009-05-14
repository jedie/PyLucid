# coding:utf-8

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response

from django.template.loader import render_to_string

from auth.forms import UsernameForm


# DEBUG is usefull for debugging password reset. It send no email, it puts the
# email text direclty into the CMS page.
#DEBUG = True
DEBUG = False
# IMPORTANT:
# Should realy only use for debugging!!!
if DEBUG:
    import warnings
    warnings.warn("Debugmode is on", UserWarning)



def http_get_view(request):
    """
    Login view
    """
    request.page_msg("TODO: refactor the rest from auth plugin ;)")
    
    if DEBUG:
        request.page_msg(
            "Warning: DEBUG is ON! Should realy only use for debugging!"
        )
    
    context = request.PYLUCID.context

    username_form = UsernameForm()
    context["form"] = username_form
    
    # return a string for replacing the normal cms page content
    return render_to_string('auth/input_username.html', context)
    
def logout(request):
    pass