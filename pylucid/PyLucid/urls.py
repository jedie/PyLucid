"""
    PyLucid.urls
    ~~~~~~~~~~~~

    The urls, manage the PyLucid CMS.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyright: 2007 by the PyLucid team.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

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
        # RUN A VIEW
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
            '^%s/$' % settings.INSTALL_URL_PREFIX,
            'PyLucid.install.index.menu'
        ),
    )
else:
    # _install section is deactivated -> start with a empty urls
    urls = ()


#______________________________________________________________________________
# The normal views:

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
    (
        r'^%s/' % settings.ADMIN_URL_PREFIX,
        include('django.contrib.admin.urls')
    ),
    #_____________________________________
    # permalink
    (
        (
            '^%s/'
            '(?P<page_id>\d+)/(.*?)$'
        ) % getattr(settings, "PERMALINK_URL_PREFIX", "_goto"),
        'PyLucid.index.permalink'
    ),
    #_____________________________________
    # CMS PAGE VIEW
    # A normal CMS page url simply consists of the page shortcuts.
    # The shortcuts contains only these chars: [a-zA-Z0-9_/-]
    (r'^([\w/-]*?)/?$', 'PyLucid.index.index'),

    #--------------------------------------------------------------------------
)


if getattr(settings, "REDIRECT_OLD_PYLUCID_URL", False):
    # Redirect old PyLucid (with "index.py") to the new URLs.
    # Only usefull, if you have a old PyLucid page used in the past ;)
    urls += (
        r'^index.py(.*?)$', 'PyLucid.index.redirect'
    ),


# serve static files
if getattr(settings, "SERVE_STATIC_FILES", False):
    # Should only enabled, if the django development server used.
    urls += (
        '^%s(?P<path>.*)$' % settings.MEDIA_URL.lstrip("/"),
        'django.views.static.serve',
        {'document_root': './%s' % settings.MEDIA_URL},
    ),


urlpatterns = patterns('', *urls)
