# coding: utf-8

"""
    PyLucid markup preview form
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django import forms

from pylucid_project.apps.pylucid.models.pagecontent import PageContent


class MarkupPreviewForm(forms.ModelForm):
    class Meta:
        model = PageContent
        fields = ('content', 'markup')
