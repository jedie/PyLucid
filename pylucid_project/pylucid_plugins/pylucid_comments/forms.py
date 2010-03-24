# coding:utf-8

from django import forms
from django.contrib.comments.forms import CommentForm
from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.models import Language

from pylucid_comments.models import PyLucidComment
from django_tools.middlewares import ThreadLocal

class PyLucidCommentForm(CommentForm):
    notify = forms.BooleanField(required=False, initial=True,
        help_text="Send me a mail if someone replay on my comment. (Needs a email address ;)"
    )
    def __init__(self, target_object, data=None, initial=None):
        """ prefill some user info """
        if initial is None:
            initial = {}

        current_user = ThreadLocal.get_current_user()
        if current_user.is_authenticated():
            initial["name"] = current_user.get_full_name() or current_user.username
            initial["email"] = current_user.email

        super(PyLucidCommentForm, self).__init__(target_object, data, initial)

    def get_comment_model(self):
        # Use our custom comment model instead of the built-in one.
        return PyLucidComment

    def get_comment_create_data(self):
        # Use the data of the superclass, and add the notify field
        data = super(PyLucidCommentForm, self).get_comment_create_data()
        if self.cleaned_data['notify'] == True and self.cleaned_data['email']:
            data['notify'] = True
        else:
            data['notify'] = False
        return data


