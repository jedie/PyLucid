# coding: utf-8

"""
    url debug
    ~~~~~~~~~
    
    used in 'show_internals' and for developing.
    
    
    For developing debug, add this to local_settings.py:
        
        import logging
        log = logging.getLogger("pylucid.url_debug")
        log.setLevel(logging.DEBUG)
        
        #handler = logging.FileHandler('url_debug.log') # log into a file
        handler = logging.StreamHandler() # log to console / stdout
        
        handler.setFormatter(logging.Formatter(
            "%(levelname)s %(asctime)s %(module)s.%(funcName)s: %(message)s"
        ))
        log.handlers = [handler] # settings.py would be import more than one time
        
        
    an this into code, e.g.:
        log_urls(hide=("/admin/", "/pylucid_admin/"))
    or:
        log_urls(only=("my_plugin_name",))
                

    :copyleft: 2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""


import re
import logging

if __name__ == "__main__":
    # test directly
    from pylucid_project.tests import init_test_env
    init_test_env()

from django.conf import settings
from django.contrib.admindocs.views import simplify_regex
from django.core.exceptions import ViewDoesNotExist
from django.core.urlresolvers import RegexURLPattern, RegexURLResolver

# see: http://www.pylucid.org/permalink/443/how-to-display-debug-information
log = logging.getLogger("pylucid.url_debug")


class UrlPatternInfo(object):
    """
    most parts borrowed from django-extensions:
    https://github.com/django-extensions/django-extensions/blob/master/django_extensions/management/commands/show_urls.py
    """
    def _get_root_urlpatterns(self):
        urlconf = __import__(settings.ROOT_URLCONF, {}, {}, [''])
        urlpatterns = urlconf.urlpatterns
        return urlpatterns

    def get_url_info(self, urlpatterns=None):
        """
        return a dict-list of the current used url patterns 
        """
        if urlpatterns is None:
            urlpatterns = self._get_root_urlpatterns()

        view_functions = self._extract_views_from_urlpatterns(urlpatterns)

        url_info = []
        for (func, regex, url_name) in view_functions:
            if hasattr(func, '__name__'):
                func_name = func.__name__
            elif hasattr(func, '__class__'):
                func_name = '%s()' % func.__class__.__name__
            else:
                func_name = re.sub(r' at 0x[0-9a-f]+', '', repr(func))
            url = simplify_regex(regex)

            url_info.append({
                'func_name': func_name,
                'module': func.__module__,
                'url_name': url_name,
                'regex': regex,
                'url': url
            })
        return url_info

    def _extract_views_from_urlpatterns(self, urlpatterns, base=''):
        """
        Return a list of views from a list of urlpatterns.
        
        Each object in the returned list is a two-tuple: (view_func, regex)
        """
        views = []
        for p in urlpatterns:
            if isinstance(p, RegexURLPattern):
                try:
                    views.append((p.callback, base + p.regex.pattern, p.name))
                except ViewDoesNotExist:
                    continue
            elif isinstance(p, RegexURLResolver):
                try:
                    patterns = p.url_patterns
                except ImportError:
                    continue
                views.extend(self._extract_views_from_urlpatterns(patterns, base + p.regex.pattern))
            elif hasattr(p, '_get_callback'):
                try:
                    views.append((p._get_callback(), base + p.regex.pattern, p.name))
                except ViewDoesNotExist:
                    continue
            elif hasattr(p, 'url_patterns') or hasattr(p, '_get_url_patterns'):
                try:
                    patterns = p.url_patterns
                except ImportError:
                    continue
                views.extend(self._extract_views_from_urlpatterns(patterns, base + p.regex.pattern))
            else:
                raise TypeError, "%s does not appear to be a urlpattern object" % p
        return views



class DebugResolve(object):
    def __init__(self, instance):
        self.instance = instance
        self.origin_resolve = instance.resolve

    def __call__(self, path):
        result = self.origin_resolve(path)
        log.debug(
            "resolve %s with %r -> %s" % (
                repr(path), self.instance.regex.pattern, repr(result)
            )
        )
        return result


def debug_log_urls(urlpatterns, base=''):
    """
    add log output to every url resolve call.
    """
    for p in urlpatterns:
        if isinstance(p, RegexURLPattern):
            log.debug("add debug to RegexURLPattern: %s" % repr(p))
            p.resolve = DebugResolve(p)
        elif isinstance(p, RegexURLResolver):
            try:
                patterns = p.url_patterns
            except ImportError:
                continue
            debug_log_urls(patterns, base + p.regex.pattern)
        else:
            log.debug("Do nothing with", p)


def log_urls(urlpatterns=None, hide=None, only=None):
    """
    e.g.:
        log_urls(hide=("/admin/", "/pylucid_admin/"))
    or:
        log_urls(only=("/<url_lang",))
    """
    if hide is not None:
        log.debug("Display urls and hide: %s" % repr(hide))
    if only is not None:
        log.debug("Display urls but only: %s" % repr(only))

    def contains(url, str_list):
        for s in str_list:
            if s in url["url"]:
                return True

    for url in UrlPatternInfo().get_url_info(urlpatterns):
        if hide is not None and contains(url, hide):
            continue
        if only is not None and not contains(url, only):
            continue
        log.debug("%s - %s" % (url["url"], url["url_name"]))


if __name__ == "__main__":
    log.setLevel(logging.DEBUG)
    log.handlers = [logging.StreamHandler()]

    log_urls(hide=("/admin/", "/pylucid_admin/"))
#     log_urls(only=("/<url_lang",))
