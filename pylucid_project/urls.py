# coding: utf-8

"""
    global url patterns
    ~~~~~~~~~~~~~~~~~~~


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author:$

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings
from django.conf.urls.defaults import patterns, url, include
from django.contrib.admin.views.decorators import staff_member_required as staff
from django.views.generic.list_detail import object_detail

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    #_____________________________________
    # DJANGO ADMIN PANEL
    (r'^%s/' % settings.ADMIN_URL_PREFIX, include(admin.site.urls)),

    ('^update/', include('apps.pylucid_update.urls')),

    ('^', include('apps.pylucid.urls')),
)

# serve static files
if settings.SERVE_STATIC_FILES:
    # Should only enabled, if the django development server used.
    urlpatterns += patterns('',
        ('^%s/(?P<path>.*)$' % settings.MEDIA_URL.strip("/"), 'django.views.static.serve',
            {'document_root': '/path/to/media', 'show_indexes': True}),
    )


