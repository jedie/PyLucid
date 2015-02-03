# coding: utf-8


from django.conf.urls import patterns, url

from pylucid_project.pylucid_plugins.blog import views

urlpatterns = patterns('',
    url(r'^tags/(?P<tags>.+?)/$', views.tag_view, name='Blog-tag_view'),

    url(r'^(?P<year>\d{4})/$',
        views.BlogYearArchiveView.as_view(), name='Blog-year_archive'
    ),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        views.BlogMonthArchiveView.as_view(), name='Blog-month_archive'
    ),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$',
        views.BlogDayArchiveView.as_view(), name='Blog-day_archive'
    ),

    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
        views.detail_view, name='Blog-detail_view'
    ),

    url(r'^(?P<id>\d+?)/(?P<slug>.*)/$', views.permalink_view, name='Blog-permalink_view'),
    url(r'^(?P<id>\d+?)/(?P<title>.*)/$', views.redirect_old_urls),

    url(r'^feed/(?P<tags>.+)/(?P<filename>.+?)$', views.feed, name='Blog-tag_feed'),
    url(r'^feed/(?P<filename>.+?)$', views.feed, name='Blog-feed'),
    url(r'^feed/', views.select_feed, name='Blog-select_feed'),

    url(r'^', views.summary, name='Blog-summary'),
)
