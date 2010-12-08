# coding: utf-8

"""
    PyLucid blog forms
    ~~~~~~~~~~~~~~~~~~

    Forms for the blog.

    :copyleft: 2008-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""


from django import forms

from pylucid_project.apps.pylucid.forms.utils import TagLanguageSitesFilter

from blog.models import BlogEntry


class BlogEntryForm(TagLanguageSitesFilter, forms.ModelForm):
    """
    Form for create/edit a blog entry.
    """
    class Meta:
        model = BlogEntry
