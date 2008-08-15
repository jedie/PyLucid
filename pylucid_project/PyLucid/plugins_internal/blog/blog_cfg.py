# -*- coding: utf-8 -*-

#_____________________________________________________________________________
# meta information
__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "A simple blog system"
__long_description__ = """
More information: http://www.pylucid.org/_goto/165/blog/
"""

#_____________________________________________________________________________
# preferences

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from PyLucid.models.Page import MARKUPS

DONT_CHECK = 0
REJECT_SPAM = 1
MODERATED = 2

ACTIONS = (
    (DONT_CHECK,    _("don't check")),
    (REJECT_SPAM,   _("reject as spam")),
    (MODERATED,     _("hide, for later moderation")),
)

class PreferencesForm(forms.Form):
    """
    Blog preferences.

    'mod_keywords' and 'spam_keywords' are case-insensitive and matches on every
    partial word. Be carefull with 'spam_keywords'.

    More information: http://www.pylucid.org/_goto/165/blog/
    """
    blog_title = forms.CharField(
        initial = "blog",
        help_text = _(
            "The blog title displays as a headline on every blog page."
        ),
    )
    description = forms.CharField(
        initial = "", required=False,
        help_text = _(
            "The blog description (Used for RSS/Atom feeds)."
        ),
    )
    language = forms.CharField(
        initial = u"en",
        help_text = _(
            "The blog language (Used for RSS/Atom feeds)."
        ),
    )
    default_markup = forms.IntegerField(
        widget=forms.Select(choices=MARKUPS),
        initial = 6,
        help_text=_("the used markup language for this entry"),
    )
    max_anonym_count = forms.IntegerField(
        initial = 10,
        min_value = 1,
        help_text=_(
            "The maximal numbers of blog entries, displayed together"
            " for anonymous users"
        ),
    )
    max_user_count = forms.IntegerField(
        initial = 30,
        min_value = 1,
        help_text=_(
            "The maximal numbers of blog entries, displayed together"
            " for logged in PyLucid users."
        ),
    )
    max_tag_feed = forms.IntegerField(
        initial = 10,
        min_value = 1,
        help_text=_(
            "The maximal numbers of tag feeds, displayed together."
        ),
    )

    max_cloud_size = forms.FloatField(
        initial = 2.0,
        min_value = 1,
        help_text=_(
            "max font size in the tag cloud (CSS 'em' unit)"
        ),
    )
    min_cloud_size = forms.FloatField(
        initial = 0.7,
        min_value = 0.1,
        help_text=_(
            "min font size in the tag cloud (CSS 'em' unit)"
        ),
    )

    notify = forms.CharField(
        initial = "\n".join(
            [i["email"] \
            for i in User.objects.filter(is_superuser=True).values("email")]
        ),
        required=False,
        help_text = _(
            "Notify these email adresses if a new comment submited"
            " (seperated by newline!)"
        ),
        widget=forms.Textarea(attrs={'rows': '5'}),
    )
    spam_notify = forms.BooleanField(
        initial = True,
        required=False,
        help_text = _("Send a notify email on every spam reject."),
    )

    mod_keywords = forms.CharField(
        initial = "\n".join((
            "www.", "://", "<", ">",
            "pr0n", "fuck", "blow", "pharmacy", "pills", "enlarge", "buy",
            "casino",
        )),
        help_text = _(
            "Keywords for auto hide a new comment, for later moderation."
            " (seperated by newline!)"
        ),
        widget=forms.Textarea(attrs={'rows': '15'}),
    )
    spam_keywords = forms.CharField(
        initial = "\n".join((
            "viagra", "penis enlarge",
        )),
        help_text = _(
            "Keywords for reject a comment submission as spam."
            " (seperated by newline!)"
        ),
        widget=forms.Textarea(attrs={'rows': '15'}),
    )

    check_referer = forms.ChoiceField(
        choices = ACTIONS,
        initial = MODERATED,
        help_text = _(
            "What to do, if http referer contains not your domain?"
        ),
    )


# They can only exist one blog in a PyLucid instance
multiple_pref = False

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

    "select_feed_format":   anonymous_rights,
    "feed":                 anonymous_rights,

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
    "edit_comment": {
        "must_login": True,
        "must_admin": True,
    },
    "delete_comment": {
        "must_login": True,
        "must_admin": True,
    },
    "mod_comments": {
        "must_login": True,
        "must_admin": False,
        "admin_sub_menu": {
            "section"       : _("blog"), # The sub menu section
            "title"         : _("moderate comments"),
            "help_text"     : _("moderate new non-public comments."),
            "open_in_window": False, # Should be create a new JavaScript window?
            "weight" : 0, # sorting weight for every section entry
        },
    },
}
