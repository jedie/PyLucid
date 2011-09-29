# coding: utf-8

"""
    PyLucid forms utils
    ~~~~~~~~~~~~~~~~~~~

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django.conf import settings

from django_tools.middlewares import ThreadLocal


class TagLanguageSitesFilter(object):
    """
    Helper class for django-tagging & django-tools jQueryTagModelField tag field:
    Display in the jQuery help_text only the tags with the same language and sites.
    
    uses in Blog and Lexicon model form
    
    Usage e.g.:
    ---------------------------------------------------------------------------
    from pylucid_project.apps.pylucid.forms.utils import TagLanguageSitesFilter
    
    class FooBarModelForm(TagLanguageSitesFilter, forms.ModelForm):
        class Meta:
            model = MyModel
    ---------------------------------------------------------------------------
    IMPORANT: TagLanguageSitesFilter must used before forms.ModelForm!
    """
    sites_filter = "sites__id__in"

    def __init__(self, *args, **kwargs):
        """
        prepare the tag queryset filter
        """
        super(TagLanguageSitesFilter, self).__init__(*args, **kwargs)

        def get_data(field_name):
            return self.initial.get(field_name, None) or self.data.get(field_name, None)

        language = get_data("language")
        if not language:
            # Use current language for tag queryset filter
            request = ThreadLocal.get_current_request()
            language = request.PYLUCID.current_language

        sites = get_data("sites")
        if not sites:
            # Use current site for tag queryset filter
            sites = [settings.SITE_ID]

        # change the tag queryset filter:
        self.fields["tags"].widget.tag_queryset_filters = {
            "language": language,
            self.sites_filter: sites,
        }



