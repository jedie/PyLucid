# -*- coding: utf-8 -*-

#_____________________________________________________________________________
# meta information
__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "A simple blog system (extermental)"
__long_description__ = """
"""

#_____________________________________________________________________________
# preferences

from django.conf import settings
from django import newforms as forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from PyLucid.models.Page import MARKUPS

class PreferencesForm(forms.Form):
    """
    Blog preferences
    """
    blog_title = forms.CharField(
        initial = "blog",
        help_text = _(
            "The blog title displays as a headline on every blog page."
        ),
    )
    default_markup = forms.IntegerField(
        widget=forms.Select(choices=MARKUPS),
        initial = 6,
        help_text=_("the used markup language for this entry"),
    )
    max_count = forms.IntegerField(
        initial = 10,
        min_value = 3,
        help_text=_("The maximal numbers of blog entries, displayed together."),
    )

    notify = forms.CharField(
        initial = "\n".join(
            [i["email"] for i in User.objects.filter(is_superuser=True).values("email")]
        ),
        help_text = _(
            "Notify these email adresses if a new comment submited"
            " (seperated by newline!)"
        ),
        widget=forms.Textarea(attrs={'rows': '5'}),
    )

    mod_keywords = forms.CharField(
        initial = (
            "http://\n"
            "www.\n"
        ),
        help_text = _(
            "Keywords for auto hide a new comment, for later moderation."
            " (seperated by newline!)"
        ),
        widget=forms.Textarea(attrs={'rows': '15'}),
    )
    spam_keywords = forms.CharField(
        initial = (
            "sex\n"
            "viagra\n"
            "porn\n"
        ),
        help_text = _(
            "Keywords for indentify a submited new comment as spam."
            " (seperated by newline!)"
        ),
        widget=forms.Textarea(attrs={'rows': '15'}),
    )

#_____________________________________________________________________________
# plugin administration data

anonymous_rights = {
    "must_login"    : False,
    "must_admin"    : False,
}

plugin_manager_data = {
    #__________________________________________________________________________
    # Public views
    "lucidTag":     anonymous_rights,
    "tag":          anonymous_rights,
    "add_comment":  anonymous_rights,
    "detail":       anonymous_rights,

    #__________________________________________________________________________
    # Restricted views

    "edit": {
        "must_login"    : True,
        "must_admin"    : False,
    },
    "delete": {
        "must_login"    : True,
        "must_admin"    : False,
    },
    "add_entry": {
        "must_login"    : True,
        "must_admin"    : False,
        "admin_sub_menu": {
            "section"       : _("blog"), # The sub menu section
            "title"         : _("Add new blog entry."),
            "help_text"     : _("Create a new blog entry."),
            "open_in_window": False, # Should be create a new JavaScript window?
            "weight" : -5, # sorting weight for every section entry
        },
    },

    "mod_comments": {
        "must_login": True,
        "must_admin": False,
        "admin_sub_menu": {
            "section"       : _("blog"), # The sub menu section
            "title"         : _("moderate comments"),
            "help_text"     : _("moderate new comments."),
            "open_in_window": False, # Should be create a new JavaScript window?
            "weight" : 0, # sorting weight for every section entry
        },
    },
}
