# coding: utf-8

"""
    PyLucid PageMeta Form
    ~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django import forms
from django.conf import settings

from django_tools.middlewares import ThreadLocal

from pylucid_project.apps.pylucid.models.pagemeta import PageMeta
from pylucid_project.apps.pylucid.models.pagetree import PageTree


class PageMetaForm(forms.ModelForm):

    def _setup_tag_filter(self):
        """
        prepare the tag queryset filter
        """
        def get_data(field_name):
            return self.initial.get(field_name, None) or self.data.get(field_name, None)

        language = get_data("language")
        if not language:
            # Use current language for tag queryset filter
            request = ThreadLocal.get_current_request()
            language = request.PYLUCID.current_language

        pagetree_id = get_data("pagetree")
        if pagetree_id:
            pagetree = PageTree.objects.only("site").get(id=pagetree_id)
            site = pagetree.site
        else:
            # Use current site for tag queryset filter
            site = settings.SITE_ID

        # change the tag queryset filter:
        self.fields["tags"].widget.tag_queryset_filters = {
            "language": language,
            "pagetree__site": site,
        }

    def __init__(self, *args, **kwargs):
        super(PageMetaForm, self).__init__(*args, **kwargs)
        self._setup_tag_filter()


    class Meta:
        model = PageMeta
