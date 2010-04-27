# coding:utf-8

from django import forms
from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.models import Language, PageContent
from blog.models import BlogEntry
from lexicon.models import LexiconEntry


from find_and_replace.preference_forms import get_preferences


CONTENT_TYPES = (
    (u"PageContent", PageContent),
    (u"BlogEntry", BlogEntry),
    (u"LexiconEntry", LexiconEntry),
)
CONTENT_TYPES_CHOICES = [(no, data[0]) for no, data in enumerate(CONTENT_TYPES)]
CONTENT_TYPES_DICT = dict([(no, data[1]) for no, data in enumerate(CONTENT_TYPES)])


class FindReplaceForm(forms.Form):
    find_string = forms.CharField()
    replace_string = forms.CharField()

    languages = forms.MultipleChoiceField()

    content_type = forms.ChoiceField(
        choices=CONTENT_TYPES_CHOICES,
        help_text=_("Please select the content type for the operation.")
    )
    simulate = forms.BooleanField(
        initial=True, required=False,
        help_text=_("Don't replace anything.")

    )

    def __init__(self, *args, **kwargs):
        super(FindReplaceForm, self).__init__(*args, **kwargs)

        preferences = get_preferences()
        self.fields["find_string"].min_length = preferences["min_term_len"]
        self.fields["find_string"].max_length = preferences["max_term_len"]

        self.fields["replace_string"].max_length = preferences["max_term_len"]

        self.fields["languages"].choices = Language.objects.get_choices()
