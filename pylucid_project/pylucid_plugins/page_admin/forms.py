# coding:utf-8

from django import forms
from django.utils.translation import ugettext as _

class EditPageForm(forms.Form):
    """
    Form for editing a cms page.
    """
    edit_comment = forms.CharField(
        max_length=255, required=False,
        help_text=_("The reason for editing."),
        widget=forms.TextInput(attrs={'class':'bigger'}),
    )

    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': '15'}),
    )