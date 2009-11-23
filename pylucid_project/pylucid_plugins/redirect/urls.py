# coding: utf-8

from django.conf.urls.defaults import patterns, url

from redirect import views

urlpatterns = patterns('',
    url(r'^(?P<rest_url>.*?)$', views.redirect, name='PluginRedirect-redirect'),

    # FIXME: This plugin should be listed on "create new plugin page"
    # The PluginPageManager().get_app_choices() used this:
    # django_tools.utils.installed_apps_utils.get_filtered_apps()
    # And this routine match only on views without kwargs!
    # So we do a work-a-round here:
    url(r'^', views.redirect_index, name='PluginRedirect-redirect-index'),
)


