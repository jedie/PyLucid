# coding:utf-8

from django import forms
from django.contrib.comments.forms import CommentForm
from django.utils.translation import ugettext as _

from pylucid.models import Language

from pylucid_comments.models import PyLucidComment

class PyLucidCommentForm(CommentForm):
    title = forms.CharField(max_length=300)
    lang = forms.ModelChoiceField(queryset=Language.objects.all(), label=_('Language'))

    def get_comment_model(self):
        # Use our custom comment model instead of the built-in one.
        return PyLucidComment

    def get_comment_create_data(self):
        # Use the data of the superclass, and add in the title field
        data = super(PyLucidCommentForm, self).get_comment_create_data()
        data['title'] = self.cleaned_data['title']
        data['lang'] = self.cleaned_data['lang']
        return data

