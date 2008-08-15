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

from django import forms
from django.utils.translation import ugettext as _

from PyLucid.tools.forms_utils import StripedCharField, ListCharField

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
    new_tags = ListCharField( # New field, (no field from BlogEntry model)
        max_length=255, required=False,
        help_text=_(
            "New tags for this entry, if there not in the list above"
            " (separated by spaces.)"
        ),
        widget=forms.TextInput(attrs={'class':'bigger'}),
    )

    def __init__(self, *args, **kwargs):
        """
        set some widget attributes
        """
        super(BlogEntryForm, self).__init__(*args, **kwargs)

        # Limit the MultipleChoiceField size
        # Is there are a better way to do this? See:
        # http://www.python-forum.de/topic-15503.html (de)
        self.fields['tags'].widget.attrs["size"] = 7

        # makes the content textarea bigger
        self.fields['content'].widget.attrs["rows"] = 15

    class Meta:
        model = BlogEntry