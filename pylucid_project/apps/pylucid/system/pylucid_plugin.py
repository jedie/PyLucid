# coding: utf-8

"""
    PyLucid plugin tools
    ~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2009-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.p

"""


from django.contrib import messages
from django.core import urlresolvers
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect

from dbpreferences.forms import DBPreferencesBaseForm


class PyLucidDBPreferencesBaseForm(DBPreferencesBaseForm):
    def get_preferences(self, request, lucidtag_kwargs):
        """
        Update the preferences dict with the given kwargs dict.
        Send a staff user feedback if a kwargs key is invalid.
        """
        preferences = super(PyLucidDBPreferencesBaseForm, self).get_preferences()
        if request.user.is_staff:
            for key in lucidtag_kwargs.keys():
                if key not in preferences:
                    messages.info(request,
                        "Keyword argument %r is invalid for lucidTag %r !" % (key, self.Meta.app_label)
                    )
        preferences.update(lucidtag_kwargs)
        return preferences


class PluginGetResolver(object):
    def __init__(self, resolver):
        self.resolver = resolver
    def __call__(self, *args, **kwargs):
        return self.resolver


def _raise_resolve_error(plugin_url_resolver, rest_url):
    tried = [i[0][0][0] for i in plugin_url_resolver.reverse_dict.values()]
#    for key, value in plugin_url_resolver.reverse_dict.values():
#        print key, value

#    tried = [prefix + pattern.regex.pattern.lstrip("^") for pattern in plugin_urlpatterns]
    raise urlresolvers.Resolver404, {'tried': tried, 'path': rest_url + "XXX"}


def call_plugin(request, url_lang_code, prefix_url, rest_url):
    """
    Call a plugin and return the response.
    used for PluginPage
    """
    lang_entry = request.PYLUCID.current_language
    pluginpage = request.PYLUCID.pluginpage
    pagemeta = request.PYLUCID.pagemeta

    # build the url prefix
    # Don't use pagemeta.language.code here, use the real url_lang_code, because of case insensitivity
    url_prefix = "^%s/%s" % (url_lang_code, prefix_url)

    # Get pylucid_project.system.pylucid_plugins instance
    plugin_instance = pluginpage.get_plugin()

    plugin_url_resolver = plugin_instance.get_plugin_url_resolver(
        url_prefix, urls_filename=pluginpage.urls_filename,
    )
    # for key, value in plugin_url_resolver.reverse_dict.items(): print key, value

    # get the plugin view from the complete url
    resolve_url = request.path_info
    result = plugin_url_resolver.resolve(resolve_url)
    if result == None:
        _raise_resolve_error(plugin_url_resolver, resolve_url)

    view_func, view_args, view_kwargs = result

    if "pylucid.views" in view_func.__module__:
        # The url is wrong, it's from PyLucid and we can get a loop!
        # FIXME: How can we better check, if the view is from the plugin and not from PyLucid???
        _raise_resolve_error(plugin_url_resolver, resolve_url)

    merged_url_resolver = plugin_instance.get_merged_url_resolver(
        url_prefix, urls_filename=pluginpage.urls_filename,
    )

    # Patch urlresolvers.get_resolver() function, so only our own resolver with urlpatterns2
    # is active in the plugin. So the plugin can build urls with normal django function and
    # this urls would be prefixed with the current PageTree url.
    old_get_resolver = urlresolvers.get_resolver
    urlresolvers.get_resolver = PluginGetResolver(merged_url_resolver)

    # Add info for pylucid_project.apps.pylucid.context_processors.pylucid
    request.plugin_name = view_func.__module__.split(".", 1)[0]  # FIXME: Find a better way!
    try:
        request.method_name = view_func.__name__
    except AttributeError:
        # e.g.: it's a django.contrib.syndication.views.Feed class instance
        request.method_name = view_func.__class__.__name__

    csrf_exempt = getattr(view_func, 'csrf_exempt', False)
    if not csrf_exempt:
        view_func = csrf_protect(view_func)

    # Call the view
    response = view_func(request, *view_args, **view_kwargs)

    if csrf_exempt and isinstance(response, HttpResponse):
        response.csrf_exempt = True

    request.plugin_name = None
    request.method_name = None

    # restore the patched function
    urlresolvers.get_resolver = old_get_resolver

    return response

