# coding: utf-8

"""
    PyLucid lexicon forms
    ~~~~~~~~~~~~~~~~~~~~~

    Forms for the lexicon.

    :copyleft: 2008-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django import forms

from pylucid_project.apps.pylucid.forms.utils import TagLanguageSitesFilter

from lexicon.models import LexiconEntry


class LexiconEntryForm(TagLanguageSitesFilter, forms.ModelForm):
    """
    Form for create/edit a lexicon entry.
    The ManyToMany field "sites" from Model would be limited with LimitManyToManyFields
    """
    class Meta:
        model = LexiconEntry
