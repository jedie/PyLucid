# coding: utf-8

"""
    PyLucid lexicon forms
    ~~~~~~~~~~~~~~~~~~

    Forms for the lexicon.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: 2009-07-14 16:14:13 +0200 (Di, 14 Jul 2009) $
    $Rev: 2111 $
    $Author: JensDiemer $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

from django import forms

# http://code.google.com/p/django-tools/
#from django_tools.forms_utils import LimitManyToManyFields

from lexicon.models import LexiconEntry


class LexiconEntryForm(forms.ModelForm):
    """
    Form for create/edit a lexicon entry.
    The ManyToMany field "sites" from Model would be limited with LimitManyToManyFields
    """
    class Meta:
        model = LexiconEntry
