# -*- coding: utf-8 -*-
"""
    PyLucid.index
    ~~~~~~~~~~~~~

    Contains all view function, except the _install views.

    - index(): Display a PyLucid CMS Page
    - handle_command(): Answer a _command Request
    - permalink(): redirect to the real page url
    - redirect(): simple redirect old PyLucid URLs to the new location.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect, \
                                                           HttpResponseRedirect
from django.conf import settings
from django.template import RequestContext, TemplateSyntaxError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from PyLucid.models import Page
from PyLucid.system import plugin_manager
from PyLucid.system.URLs import URLs
from PyLucid.system.response import SimpleStringIO
from PyLucid.system.exceptions import AccessDenied
from PyLucid.system.context_processors import add_dynamic_context, add_css_tag
from PyLucid.tools.utils import escape, escape_django_tags
from PyLucid.tools.content_processors import apply_markup, \
                                                        render_string_template
from PyLucid.plugins_internal.page_style.page_style import replace_add_data



# TODO: Remove in PyLucid >v0.8.5
PAGE_MSG_INFO_LINK = (
    '<a href="'
    'http://www.pylucid.org/_goto/121/changes/#20-05-2008-page_msg'
    '">pylucid.org - Backwards-incompatible changes - page_msg</a>'
)

def _redirect_to_login(request):
    """
    Redirect to the _comment auth login with the default page
    FIXME: We should build the auth command url in a better way.
    """
    path = "/%s/%s/auth/login/?next=%s" % (
        settings.COMMAND_URL_PREFIX, Page.objects.default_page.id, request.path
    )
    return HttpResponseRedirect(path)

def _redirect_access_denied(request):
    """
    Redirect to login page, if the user is anonymous.
    """
    if not request.user.is_anonymous():
        # The user is logged in. But he hasn't the rights to see the page
        # or run the plugin method
        raise AccessDenied("User can see this page content!")

    return _redirect_to_login(request)


def _render_cms_page(request, context, page_content=None):
    """
    render the cms page.
    - render a normal cms request
    - render a _command request: The page.content is the output from the plugin.
    """
    if request.anonymous_view == False:
        # TODO: remove in v0.9, see: ticket:161
        # context["robots"] was set in contex_processors.static()
        # Hide the response from search engines
        context["robots"] = "NONE,NOARCHIVE"

    context["anonymous_view"] = request.anonymous_view

    current_page = context["PAGE"]

    if page_content:
        # The page content comes e.g. from the _command plugin
#        current_page.content = page_content
        page_content = escape_django_tags(page_content)
    else:
        # get the current page data from the db
        page_content = current_page.content

        markup_no = current_page.markup
        page_content = apply_markup(page_content, context, markup_no)

    # Render only the CMS page content:
    try:
        page_content = render_string_template(page_content, context)
        # If a user access a public viewable cms page, but in the page content
        # is a lucidTag witch is a restricted method, the pylucid plugin
        # manager would normaly raise a AccessDenied.
        # The Problem is, if settings.TEMPLATE_DEBUG is on, we didn't get a
        # AccessDenied directly, we always get a TemplateSyntaxError! All
        # other errors will catched and raised a TemplateSyntaxError, too.
        # See django/template/debug.py
        # TODO: Instead of a redirect to the login command, we can insert
        # the ouput from auth.login directly
    except TemplateSyntaxError, err:
        # Check if it was a AccessDenied exception
        # sys.exc_info() added in django/template/debug.py
        error_class = err.exc_info[1]
        if isinstance(error_class, AccessDenied):
            return _redirect_access_denied(request)
        else:
            raise # raise the original error
    except AccessDenied:
        # settings.TEMPLATE_DEBUG is off
        return _redirect_access_denied(request)

    # http://www.djangoproject.com/documentation/templates_python/#filters-and-auto-escaping
    page_content = mark_safe(page_content) # turn djngo auto-escaping off

    context["PAGE"].content = page_content

    template = current_page.template
    template_content = template.content

    # Render the Template to build the complete html page:
    content = render_string_template(template_content, context)

    # insert JS/CSS data from any Plugin *after* the page rendered with the
    # django template engine:
    content = replace_add_data(context, content)

    # TODO: Remove in PyLucid >v0.8.5
    middleware = 'PyLucid.middlewares.pagemessages.PageMessagesMiddleware'
    if middleware not in settings.MIDDLEWARE_CLASSES:
        msg = (
            u"ERROR: %s not in settings.MIDDLEWARE_CLASSES!"
            " More info: %s"
        ) % (middleware, PAGE_MSG_INFO_LINK)
        content = content.replace(u"<!-- page_messages -->", msg)

    return HttpResponse(content)




def _get_context(request, current_page_obj):
    """
    Setup the context with PyLucid objects.
    For index() and handle_command() views.
    """
    # add additional attribute
    request.anonymous_view = True

    context = RequestContext(request)

    context["PAGE"] = current_page_obj
    context["URLs"] = URLs(context)
#    context["URLs"].debug()

    # For additional JavaScript and StyleSheet information.
    # JS+CSS from internal_pages or CSS data for pygments
    # Add into the context object. Would be integraged in the page with the
    # additional_content middleware.
    context["js_data"] = []
    context["css_data"] = []

    # A list of every used html DIV CSS-ID.
    # used in PyLucid.defaulttags.lucidTag.lucidTagNode._add_unique_div()
    context["CSS_ID_list"] = []

    # add dynamic content into the context (like: login/logout link)
    add_dynamic_context(request, context)

    # Add the context to the reponse object.
    # Used in PyLucid middlewares
    request.CONTEXT = context

    # TODO: Remove in PyLucid >v0.8.5
    msg = 'Error, see: %s' % PAGE_MSG_INFO_LINK
    context["messages"] = [mark_safe(msg)]

    return context


def index(request, url):
    """
    The main index method.
    Return a normal cms page request.
    Every Request will be cached for anonymous user. For the cache_key we use
    the page shortcut from the url.
    """
    try:
        current_page_obj = Page.objects.get_by_shortcut(url, request.user)
    except Page.DoesNotExist:
        raise Http404(_("Page '%s' doesn't exists.") % url)
    except Page.objects.WrongShortcut, correct_url:
        # Some parts of the URL was wrong, but we found a right page
        # shortcut -> redirect to the right url
        return HttpResponseRedirect(correct_url)
    except AccessDenied:
        if request.user.is_anonymous():
            # FIXME: We should build the auth command url in a better way.
            return _redirect_to_login(request)
        else:
            # User is logged in but access is denied,
            # probably due to group restrictions.
            request.user.message_set.create(message=_("Access denied"))
            new_url = Page.objects.default_page.get_absolute_url()
            return HttpResponseRedirect(new_url)

    context = _get_context(request, current_page_obj)

    # Get the response for the requested cms page:
    response = _render_cms_page(request, context)

    if getattr(request, "_use_cache", None) == None:
        # Set _use_cache information for the PyLucid cache middleware, but only
        # if it was set to true or false in the past
        request._use_cache = True

    return response


def _get_page(request, page_id):
    """
    returns the page object.
    TODO: Check int(page_id)!
    """
    try:
        current_page_obj = Page.objects.get(id=int(page_id))
    except Page.DoesNotExist:
        # The ID in the url is wrong -> goto the default page
        current_page_obj = Page.objects.default_page

        user = request.user
        if user.is_authenticated():
            # The page_msg system is not initialized, yet. So we must use the
            # low level message_set method, but this ony exist for user how are
            # login.
            # ToDo: How can we sent a message to anonymous users?
            user.message_set.create(
                message=_(
                    "Error: The page ID in the url is wrong."
                    " (goto default page.)"
                )
            )

    return current_page_obj


def handle_command(request, page_id, module_name, method_name, url_args):
    """
    handle a _command request
    """
    current_page_obj = _get_page(request, page_id)

    context = _get_context(request, current_page_obj)

    local_response = SimpleStringIO()

    if url_args == "":
        url_args = ()
    else:
        url_args = (url_args,)

    try:
        output = plugin_manager.handle_command(
            context, local_response, module_name, method_name, url_args
        )
    except AccessDenied:
        if request.debug:
            # don't use errorhandling -> raise the prior error
            raise
        page_content = "[Permission Denied!]"
    else:
        if output == None:
            # Plugin/Module has retuned the locale StringIO response object
            page_content = local_response.getvalue()
        elif isinstance(output, basestring):
            page_content = output
        elif isinstance(output, HttpResponse):
            # e.g. send a file directly back to the client
            return output
        else:
            msg = (
                "Error: Wrong output from Plugin!"
                " - It should be write into the response object"
                " or return a String/HttpResponse object!"
                " - But %s.%s has returned: %s (%s)"
            ) % (
                module_name, method_name,
                escape(repr(output)), escape(str(type(output)))
            )
            raise AssertionError(msg)

#    print module_name, method_name
#    print page_content
#    print "---"

    if page_content:
        # Add the CSS Info, but only if the plugin has returned content and
        # not when the normal cms page rendered.
        page_content = add_css_tag(
            context, page_content, module_name, method_name
        )

    return _render_cms_page(request, context, page_content)


def redirect(request, url):
    """
    simple redirect old PyLucid URLs to the new location.
    old url:
        ".../index.py/PageShortcut/"
    new url:
        ".../PageShortcut/"
    """
    if url == "":
        url = "/"

    return HttpResponsePermanentRedirect(url)


def permalink(request, page_id):
    """
    redirect to the real page url.
    """
    current_page_obj = _get_page(request, page_id)
    url = current_page_obj.get_absolute_url()
    return redirect(request, url)
