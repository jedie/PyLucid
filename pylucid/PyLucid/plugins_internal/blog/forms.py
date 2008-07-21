# -*- coding: utf-8 -*-

"""
    PyLucid blog forms
    ~~~~~~~~~~~~~~~~~~

    Forms for the blog.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

from django import newforms as forms
from django.utils.translation import ugettext as _

from PyLucid.tools.newforms_utils import StripedCharField

# from blog plugin
from PyLucid.plugins_internal.blog.models import BlogComment, BlogEntry


class BlogCommentForm(forms.ModelForm):
    """
    Add a new comment.
    """
    person_name = forms.CharField(
        min_length=4, max_length=50,
        help_text=_("Your name."),
    )
    content = StripedCharField(
        label = _('content'), min_length=5, max_length=3000,
        help_text=_("Your comment to this blog entry."),
        widget=forms.Textarea(attrs={'rows': '15'}),
    )

    class Meta:
        model = BlogComment
        # Using a subset of fields on the form
        fields = ('person_name', 'email', "homepage")


class AdminCommentForm(BlogCommentForm):
    """
    Form for editing a existing comment. Only for Admins
    """
    class Meta:
        model = BlogComment
        fields = (
            'ip_address', 'person_name', 'email', "homepage",
            "content", "is_public",
            "createtime", "lastupdatetime", "createby", "lastupdateby"
        )


class BlogEntryForm(forms.ModelForm):
    """
    Form for create/edit a blog entry.
    """
    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': '15'}),
    )

    tags = forms.CharField(
        max_length=255, required=False,
        help_text=_("Tags for this entry (separated by spaces.)"),
        widget=forms.TextInput(attrs={'class':'bigger'}),
    )
    class Meta:
        model = BlogEntry