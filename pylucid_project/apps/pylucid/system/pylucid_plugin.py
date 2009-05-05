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

import sys

from django import http
from django.conf import settings
from django.http import HttpResponse
from django.core import urlresolvers
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
    method_name = settings.PYLUCID.HTML_GET_VIEW_NAME
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
    # Get the information witch django app would be used
    pluginpage = PluginPage.objects.get(page=request.PYLUCID.pagetree)
    app_label = pluginpage.app_label
    plugin_urlconf_name = app_label + ".urls"
    
    # Get the urlpatterns from the plugin urls.py
    plugin_urlpatterns = import_module(plugin_urlconf_name).urlpatterns
    
    # build the url prefix
    prefix = "^" + prefix_url
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
    
#    for key in resolver.reverse_dict:
#        print key, resolver.reverse_dict[key]

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