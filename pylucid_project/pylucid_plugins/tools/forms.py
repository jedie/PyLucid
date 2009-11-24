# coding: utf-8

from django import forms

from pygments.lexers._mapping import LEXERS


class HighlightCodeForm(forms.Form):
    sourcecode = forms.CharField(widget=forms.Textarea)
    source_type = forms.ChoiceField(choices=sorted([(aliases[0], name) for _, name, aliases, _, _ in LEXERS.itervalues()]))

