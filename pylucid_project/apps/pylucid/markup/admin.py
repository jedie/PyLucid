# coding: utf-8

"""
    PyLucid markup ajax preview admin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.conf.urls import patterns

from pylucid_project.apps.pylucid.markup.views import markup_preview


class MarkupPreview(object):
    """
    For Admin class inherit
    """
    save_on_top = True

    def ajax_markup_preview(self, request, object_id):
        return markup_preview(request)

    def get_urls(self):
        urls = super(MarkupPreview, self).get_urls()
        my_urls = patterns('',
            (r'^(.+?)/preview/$', self.admin_site.admin_view(self.ajax_markup_preview)),
        )
        return my_urls + urls



