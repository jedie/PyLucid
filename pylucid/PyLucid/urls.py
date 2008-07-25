"""
    PyLucid.urls
    ~~~~~~~~~~~~

    The urls, manage the PyLucid CMS.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.contrib import admin
from django.conf.urls.defaults import include, patterns

from django.conf import settings

handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'

#______________________________________________________________________________
# The install section:

# We insert the _install URLs only, if the _install section is activated.
if settings.ENABLE_INSTALL_SECTION == True:
    urls = (
        #_____________________________________
        # RUN A INSTALL VIEW
        (
            (
                '^%s/'
                '(?P<module_name>[^/]*?)/'
                '(?P<method_name>[^/]*?)/'
                '(?P<url_args>.*?)$'
            ) % settings.INSTALL_URL_PREFIX,
            "PyLucid.install.index.run_method",
        ),
        #_____________________________________
        # LOGOUT
        (
            '^%s/logout/$' % settings.INSTALL_URL_PREFIX,
            'PyLucid.install.index.logout'
        ),
        #_____________________________________
        # INSTALL MENU
        (
            '^%s' % settings.INSTALL_URL_PREFIX,
            'PyLucid.install.index.menu'
        ),
    )
else:
    # _install section is deactivated -> start with a empty urls
    urls = ()


#______________________________________________________________________________
# The normal views:

# DJANGO ADMIN PANEL urls
admin.autodiscover()

urls += (
    #_____________________________________
    # COMMAND VIEW
    (
        (
            '^%s/'
            '(?P<page_id>\d+)/'
            '(?P<module_name>[^/]*?)/'
            '(?P<method_name>[^/]*?)/'
            '(?P<url_args>.*?)$'
        ) % settings.COMMAND_URL_PREFIX,
        'PyLucid.index.handle_command'
    ),
    #_____________________________________
    # DJANGO ADMIN PANEL
    (r'^%s/(.*)' % settings.ADMIN_URL_PREFIX, admin.site.root),
    #_____________________________________
    # permalink
    (
        (
            '^%s/'
            '(?P<page_id>\d+)/(.*?)$'
        ) % getattr(settings, "PERMALINK_URL_PREFIX", "_goto"),
        'PyLucid.index.permalink'
    ),
)


#______________________________________________________________________________
# Dynamic urls:

if getattr(settings, "REDIRECT_OLD_PYLUCID_URL", False):
    # Redirect old PyLucid (with "index.py") to the new URLs.
    # Only usefull, if you have a old PyLucid page used in the past ;)
    urls += (r'^index.py(.*?)$', 'PyLucid.index.redirect'),


# serve static files
if getattr(settings, "SERVE_STATIC_FILES", False):
    # Should only enabled, if the django development server used.
    urls += (
        '^%s(?P<path>.*)$' % settings.MEDIA_URL.lstrip("/"),
        'django.views.static.serve',
        {'document_root': './%s' % settings.MEDIA_URL},
    ),


#______________________________________________________________________________
# normal CMS page view

# Important: This entry must be as the last!
# A normal CMS page url simply consists of the page shortcuts.
# The shortcuts contains only these chars: [a-zA-Z0-9_/-]
urls += (r'([\w/-]*)', 'PyLucid.index.index'),


urlpatterns = patterns('', *urls)
