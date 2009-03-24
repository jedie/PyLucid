# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib.admin.views.decorators import staff_member_required as staff
from django.views.generic.list_detail import object_detail

from django.contrib import admin
from pylucid_project.apps.pylucid.urls import dynamic_cms_urls

urlpatterns = patterns('',
    #_____________________________________
    # DJANGO ADMIN PANEL
    (r'^%s/(.*)' % settings.ADMIN_URL_PREFIX, admin.site.root),
    
    
)

"""
FIXME: So einfach geht es nicht wirklich. Funktioniert zwar schon, aber ich denke, 
die urls werden nur einmal beim start der Instanz initialisiert. Wenn man also eine CMS
Seite hinzufügt, sieht man sie erst in den urls, nachdem der z.B. fastCGI Prozess neu gestartet
ist, oder?
"""
urlpatterns += dynamic_cms_urls()

# serve static files
if getattr(settings, "SERVE_STATIC_FILES", False):
    # Should only enabled, if the django development server used.
    urlpatterns += patterns('',
        '^%s/(?P<path>.*)$' % settings.MEDIA_URL.strip("/"),
        'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}
    )

admin.autodiscover()