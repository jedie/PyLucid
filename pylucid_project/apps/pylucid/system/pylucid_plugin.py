# coding: utf-8

"""
    PyLucid plugin tools
    ~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.p

"""

__version__= "$Rev:$"

import re
import sys

from django import http
from django.conf import settings
from django.http import HttpResponse
from django.core import urlresolvers
from django.utils.encoding import smart_str
from django.utils.importlib import import_module
from django.conf.urls.defaults import patterns, url

from pylucid.models import PluginPage
from pylucid.system import pylucid_objects


def call_plugin_view(request, plugin_name, method_name, method_kwargs={}):
    """
    """
    # callback is either a string like 'foo.views.news.stories.story_detail'
    callback = "pylucid_plugins.%s.views.%s" % (plugin_name, method_name)
    try:
        callable = urlresolvers.get_callable(callback)
    except (ImportError, AttributeError), err:
        raise GetCallableError(err)
    
    # Add info for pylucid_project.apps.pylucid.context_processors.pylucid
    request.plugin_name = plugin_name
    request.method_name = method_name
    
    # call the plugin view method
    response = callable(request, **method_kwargs)
    
    return response

class GetCallableError(Exception):
    pass


def call_get_views(request):
    """ call a pylucid plugin "html get view" and return the response. """
    method_name = settings.PYLUCID.HTTP_GET_VIEW_NAME
    for plugin_name in request.GET.keys():
        try:
            response = call_plugin_view(request, plugin_name, method_name)
        except GetCallableError, err:
            # plugin or view doesn't exist -> ignore get parameter
            if settings.DEBUG:
                request.page_msg(
                    "Error getting view %s.%s: %s" % (plugin_name, method_name, err))
            continue
        except:
            # insert more information into the traceback
            etype, evalue, etb = sys.exc_info()
            evalue = etype('Error rendering plugin view "%s.%s": %s' % (plugin_name, method_name, evalue))
            raise etype, evalue, etb
        
        return response



class PluginGetResolver(object):
    def __init__(self, resolver):
        self.resolver = resolver
    def __call__(self, *args, **kwargs):
        return self.resolver

def _raise_resolve_error(prefix, plugin_urlpatterns, rest_url):
    tried = [prefix + pattern.regex.pattern.lstrip("^") for pattern in plugin_urlpatterns]
    raise urlresolvers.Resolver404, {'tried': tried, 'path': rest_url}

def call_plugin(request, prefix_url, rest_url):
    """ Call a plugin and return the response. """
    lang_entry = request.PYLUCID.lang_entry
    
    # Get the information witch django app would be used
    pluginpage = PluginPage.objects.get(page=request.PYLUCID.pagetree, lang=lang_entry)
    app_label = pluginpage.app_label
    plugin_urlconf_name = app_label + ".urls"
    
    # Get the urlpatterns from the plugin urls.py
    plugin_urlpatterns = import_module(plugin_urlconf_name).urlpatterns
    
    # build the url prefix
    prefix = "^%s/%s" % (lang_entry.code, prefix_url)
    if not prefix_url.endswith("/"):
        prefix += "/"

    # The used urlpatterns
    urlpatterns2 = patterns('', url(prefix, [plugin_urlpatterns]))
    #print urlpatterns2
    
    # Append projects own url patterns, so the plugin can reverse url from them, too.
    current_urlpatterns = import_module(settings.ROOT_URLCONF).urlpatterns
    urlpatterns2 += current_urlpatterns
    
    # Make a own url resolver
    resolver = urlresolvers.RegexURLResolver(r'^/', urlpatterns2)
    
    #for key in resolver.reverse_dict:
    #    print key, resolver.reverse_dict[key]

    # get the plugin view from the complete url
    resolve_url = request.path_info
    result = resolver.resolve(resolve_url)
    if result == None:
        _raise_resolve_error(prefix, plugin_urlpatterns, rest_url)
    
    view_func, view_args, view_kwargs = result

    if "pylucid.views" in view_func.__module__:
        # The url is wrong, it's from PyLucid and we can get a loop!
        # FIXME: How can we better check, if the view is from the plugin and not from PyLucid???
        _raise_resolve_error(prefix, plugin_urlpatterns, rest_url)
    
    # Patch urlresolvers.get_resolver() function, so only our own resolver with urlpatterns2
    # is active in the plugin. So the plugin can build urls with normal django function and
    # this urls would be prefixed with the current PageTree url.
    old_get_resolver = urlresolvers.get_resolver
    urlresolvers.get_resolver = PluginGetResolver(resolver)
    
    #FIXME: Some plugins needs a "current pagecontent" object!
    #request.PYLUCID.pagecontent = 
    
    # Call the view
    response = view_func(request, *view_args, **view_kwargs)
    
    # restore the patched function
    urlresolvers.get_resolver = old_get_resolver
    
    return response


#______________________________________________________________________________
# ContextMiddleware functions

TAG_RE = re.compile("<!-- ContextMiddleware (.*?) -->", re.UNICODE)
from django.utils.importlib import import_module
from django.utils.functional import memoize

_middleware_class_cache = {}

def _get_middleware_class(plugin_name):
    plugin_name = plugin_name.encode('ascii') # check non-ASCII strings
    
    mod_name = "pylucid_plugins.%s.context_middleware" % plugin_name
    module = import_module(mod_name)
    middleware_class = getattr(module, "ContextMiddleware")
    return middleware_class
_get_middleware_class = memoize(_get_middleware_class, _middleware_class_cache, 1)


def context_middleware_request(request):
    """
    get from the template all context middleware plugins and call the request method.
    """
    context = request.PYLUCID.context
    page_template = request.PYLUCID.page_template
    
    context["context_middlewares"] = {}
    
    plugin_names = TAG_RE.findall(page_template)
    for plugin_name in plugin_names:
        # Get the middleware class from the plugin
        try:
            middleware_class = _get_middleware_class(plugin_name)
        except ImportError, err:
            request.page_msg.error("Can't import context middleware '%s': %s" % (plugin_name, err))
            continue
        
        # make a instance 
        instance = middleware_class(request, context)
        # Add it to the context
        context["context_middlewares"][plugin_name] = instance

def context_middleware_response(request, response):
    """
    replace the context middleware tags in the response, with the plugin render output
    """
    context = request.PYLUCID.context
    context_middlewares = context["context_middlewares"]
    def replace(match):
        plugin_name = match.group(1)
        try:
            middleware_class_instance = context_middlewares[plugin_name]
        except KeyError, err:
            return "[Error: context middleware %r doesn't exist!]" % plugin_name
        
        response = middleware_class_instance.render()
        if response == None:
            return ""
        elif isinstance(response, unicode):
            return smart_str(response, encoding=settings.DEFAULT_CHARSET)
        elif isinstance(response, str):
            return response
        elif isinstance(response, http.HttpResponse):
            return response.content
        else:
            raise RuntimeError(
                "plugin context middleware render() must return"
                " http.HttpResponse instance or a basestring or None!"
            )
    
    # FIXME: A HttpResponse allways convert unicode into string. So we need to do that here:
    # Or we say, context render should not return a HttpResponse?
#    from django.utils.encoding import smart_str
#    complete_page = smart_str(complete_page)
    
    source_content = response.content
    
    new_content = TAG_RE.sub(replace, source_content)
    response.content = new_content
    return response

        