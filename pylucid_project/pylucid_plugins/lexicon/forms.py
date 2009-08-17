# -*- coding: utf-8 -*-

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
from django.utils.translation import ugettext as _

import tagging # http://code.google.com/p/django-tagging/

from lexicon.models import LexiconEntry


class LexiconEntryForm(forms.ModelForm):
    """
    Form for create/edit a lexicon entry.
    """
    class Meta:
        model = LexiconEntry
        exclude = ("site",)
