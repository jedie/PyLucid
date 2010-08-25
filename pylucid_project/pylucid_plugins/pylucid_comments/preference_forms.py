# coding: utf-8

from django import forms
from django.utils.translation import ugettext_lazy as _

from django_tools.fields.sign_separated import SignSeparatedFormField

from dbpreferences.forms import DBPreferencesBaseForm


class PyLucidCommentsPrefForm(DBPreferencesBaseForm):
    ban_limit = forms.IntegerField(
        help_text=_("Number of pause errors after IP would be banned."),
        initial=3, min_value=1, max_value=100
    )
    min_pause = forms.IntegerField(
        help_text=_("Minimum pause in seconds between two comments (Used 'REMOTE_ADDR' + username)"),
        initial=60, min_value=1, max_value=600
    )
    spam_keywords = SignSeparatedFormField(
        separator=",", strip_items=True, skip_empty=True,
        initial=[
            "www.", "://", "<", ">",
            "pr0n", "fuck", "blow", "pharmacy", "pills", "enlarge", "buy",
            "casino",
        ],
        help_text=_("Keywords for auto hide a new comment, for later moderation. (Comma seperated)"),
    )
    admins_notification = forms.BooleanField(
        initial=True,
        help_text=_("Email every settings.ADMINS after a new comment submitted."),
    )
    class Meta:
        app_label = 'pylucid_comments'
