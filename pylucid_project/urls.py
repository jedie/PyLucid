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
    # PYLUCID UPDATE SECTION
    ('^%s/update/' % settings.ADMIN_URL_PREFIX, include('pylucid_update.urls')),

    #_____________________________________
    # PYLUCID ADMIN
    (r'^%s/' % settings.ADMIN_URL_PREFIX, include('pylucid_admin.urls')),

    #_____________________________________
    # DJANGO ADMIN PANEL
    (r'^%s/' % settings.ADMIN_URL_PREFIX, include(admin.site.urls)),
)

# serve static files
if settings.SERVE_STATIC_FILES:
    # Should only enabled, if the django development server used.
    print "Serve static file from MEDIA_ROOT:", settings.MEDIA_ROOT
    urlpatterns += patterns('',
        ('^%s/(?P<path>.*)$' % settings.MEDIA_URL.strip("/"), 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )

urlpatterns += patterns('',
        ('^', include('pylucid.urls')),
)

#_____________________________________________________________________________
# use the undocumented django function to add the "lucidTag" to the tag library.
# 
from django.template import add_to_builtins
add_to_builtins('pylucid_project.apps.pylucid.defaulttags')
