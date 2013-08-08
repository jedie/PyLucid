# coding: utf-8

"""
    PyLucid app url patterns
    ~~~~~~~~~~~~~~~~~~~~~~~~

    ?P<url_lang_code> is in Accept-Language header format, from RFC 2616, section 14.4 and 3.9.
    See also:
        django.utils.translation.trans_real.accept_language_re

    :copyleft: 2009-2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.conf import settings
from django.conf.urls import patterns, url

from pylucid_project.apps.pylucid import views


urlpatterns = patterns('',
    url(r'^$', views.root_page, name='PyLucid-root_page'),

    url(r'^%s/(?P<page_id>\d+)?/(?P<url_rest>.*?)$' % settings.PYLUCID.PERMALINK_URL_PREFIX, views.permalink,
        name='PyLucid-permalink'
    ),

    url(r'^%s/(?P<filepath>[\w/\.-]{4,})$' % settings.PYLUCID.HEAD_FILES_URL_PREFIX, views.send_head_file,
        name='PyLucid-send_head_file'
    ),

    # url_lang_code must match to all variantes of django.conf.global_settings.LANGUAGES
    url(r'^(?P<url_lang_code>[A-Za-z]{2}(?:-[A-Za-z]{2,4})*)/(?P<url_path>.+?)$',
        views.render_page, name='PyLucid-render_page'
    ),
    url(r'^(?P<url_slugs>.+?)/$',
        views.redirect_to_lang_url, name='PyLucid-redirect_to_lang_url'
    ),
)
