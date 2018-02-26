
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from cms.sitemaps import CMSSitemap

# admin.autodiscover()
#
#
# urlpatterns = i18n_patterns('',
#     url(r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),
#
#     url(r'^admin/', include(admin.site.urls)),  # NOQA
#     url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap',
#         {'sitemaps': {'cmspages': CMSSitemap}}),
#
#     # for djangocms-blog
#     url(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
#
#     url(r'^', include('cms.urls')),
# )
#
# # This is only needed when using runserver.
# if settings.DEBUG:
#     if 'debug_toolbar' in settings.INSTALLED_APPS:
#         import debug_toolbar
#         urlpatterns = [
#             url(r'^__debug__/', include(debug_toolbar.urls)),
#         ] + urlpatterns
#
#     urlpatterns = [
#             url(r'^media/(?P<path>.*)$', 'django.views.static.serve',  # NOQA
#                 {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
#         ] + staticfiles_urlpatterns() + urlpatterns  # NOQA








# coding: utf-8

from django.conf import settings
from django.conf.urls import include, static, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin

admin.autodiscover()


urlpatterns = i18n_patterns(
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('cms.urls')),
)

if settings.DEBUG:
    urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
