# coding: utf-8

"""
    PyLucid blog forms
    ~~~~~~~~~~~~~~~~~~

    Forms for the blog.

    :copyleft: 2008-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""


from django import forms
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from pylucid_project.apps.pylucid.forms.utils import TagLanguageSitesFilter

from pylucid_project.pylucid_plugins.blog.models import BlogEntryContent


class BlogContentForm(forms.ModelForm):
    class Meta:
        model = BlogEntryContent
        exclude = ("entry",)

class BlogForm(TagLanguageSitesFilter, forms.ModelForm):
    """
    Form for create/edit a blog entry.
    """
    sites_filter = "entry__sites__id__in"
    sites = forms.MultipleChoiceField(
        # choices= Set in __init__, so the Queryset would not execute at startup
        help_text=_("On which site should this entry exists?")
    )

    def __init__(self, *args, **kwargs):
        super(BlogForm, self).__init__(*args, **kwargs)
        self.fields["sites"].choices = Site.objects.all().values_list("id", "name")

    class Meta:
        model = BlogEntryContent
        exclude = ("entry",)
