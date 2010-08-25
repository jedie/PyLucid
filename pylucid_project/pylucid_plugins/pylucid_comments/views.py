# coding: utf-8

"""
    PyLucid page comments plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    TODO:
     * Update existing unittest (e.g. blog, lexicon)

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.p

"""

from django.db import models
from django.conf import settings
from django.contrib import messages
from django.contrib.comments.signals import comment_will_be_posted, comment_was_posted
from django.contrib.comments.views.comments import post_comment
from django.http import HttpResponse, HttpResponseBadRequest,\
    HttpResponseRedirect
from django.contrib import comments
from django.utils.translation import ugettext as _

from django_tools.decorators import render_to
from django_tools.utils.client_storage import ClientCookieStorage, InvalidCookieData

from pylucid_project.apps.pylucid.models import LogEntry


COOKIE_KEY = "comments_data" # Used to store anonymous user information

# Important: The sign may not occur in a email address or in a homepage url!
# But it can occur in the username ;)
COOKIE_DELIMITER = ";"  


#def comment_will_be_posted_handler(sender, **kwargs):
#    request = kwargs["request"]
#    comment = kwargs["comment"]
#    print comment.comment
#    print "comment_will_be_posted_handler", kwargs.keys()
    
    
    
def comment_was_posted_handler(sender, **kwargs):
#    print "comment_was_posted_handler", kwargs.keys()
    request = kwargs["request"]
    comment = kwargs["comment"]
    messages.success(request, _("Your comment has been saved."))

#comment_will_be_posted.connect(comment_will_be_posted_handler)
comment_was_posted.connect(comment_was_posted_handler)


def _bad_request(debug_msg):
    """
    Create a new LogEntry and return a HttpResponseBadRequest
    """   
    LogEntry.objects.log_action(
        app_label="pylucid_plugin.pylucid_comments", action="error", message=debug_msg,
    )
    if settings.DEBUG:
        msg = debug_msg
    else:
        msg = ""

    return HttpResponseBadRequest(msg)


@render_to("pylucid_comments/comment_form.html")
def _get_form(request):
    """ Send the comment form to via AJAX request """
    if request.is_ajax() != True:
        return _bad_request("Wrong request")  

    try:
        ctype = request.POST["content_type"].split(".", 1)
        model = models.get_model(*ctype)
    except Exception, err:
        return _bad_request("Wrong content type: %s" % err)
    
    try:
        object_pk = request.POST["object_pk"]
        target = model._default_manager.using(None).get(pk=object_pk)
    except Exception, err:
        return _bad_request("Wrong object_pk: %s" % err)

    data = {}
    if not request.user.is_authenticated():    
        # Get user data from secure cookie, set in the past, see _form_submission()
        c = ClientCookieStorage(cookie_key=COOKIE_KEY)
        try:
            raw_data = c.get_data(request)
        except InvalidCookieData, err:
            return _bad_request("Wrong cookie data: %s" % err)
            
        if raw_data is not None:
            try:
                username, email, url = raw_data.rsplit(COOKIE_DELIMITER,2)
            except ValueError, err:
                debug_msg = "Error split user cookie data: %r with %r" % (raw_data, COOKIE_DELIMITER)
                LogEntry.objects.log_action(
                    app_label="pylucid_plugin.pylucid_comments", action="error", message=debug_msg,
                )
                if settings.DEBUG:
                    raise
            else:
                data = {"name": username, "email": email, "url": url}
    
    form = comments.get_form()(target, initial=data)
    
    return {"form":form}


def _form_submission(request):
    """ Handle a AJAX comment form submission """
    if request.is_ajax() != True:
        return _bad_request("Wrong request")
      
    # Use django.contrib.comments.views.comments.post_comment to handle a comment post.
    response = post_comment(request)
    if isinstance(response, HttpResponseRedirect):
        # reload the page after comment saved via JavaScript
        response = HttpResponse("reload")
        
        if not request.user.is_authenticated(): 
            # Store user data for anonymous users in a secure cookie, used in _get_form() to pre fill the form
            comments_data = COOKIE_DELIMITER.join([
                request.POST["name"], request.POST.get("email", ""), request.POST.get("url", "")
            ])
            # Store the user data with a security hash
            c = ClientCookieStorage(cookie_key=COOKIE_KEY)
            response = c.save_data(comments_data, response)
       
    return response




def http_get_view(request):
    """
    Login+Logout view via GET parameters
    """
    action = request.GET["pylucid_comments"]

    if action == "get_form":
        return _get_form(request)
    elif action == "submit":
        return _form_submission(request)
    else:
        debug_msg = "Wrong get view parameter!"
        return _bad_request(debug_msg) # Return HttpResponseBadRequest


@render_to("pylucid_comments/comments.html")
def lucidTag(request):
    object2comment = request.PYLUCID.object2comment
    form = comments.get_form()(object2comment)
    context = {
        "form":form,
        "object2comment": object2comment,
    }
    return context
    