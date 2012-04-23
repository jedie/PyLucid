# coding:utf-8

from django import forms
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _

from dbtemplates.models import Template as DBTemplate

from pylucid_project.apps.pylucid.models import Language, PageContent, EditableHtmlHeadFile

from blog.models import BlogEntryContent
from lexicon.models import LexiconEntry


from find_and_replace.preference_forms import get_preferences


CONTENT_TYPES = (
    (u"PageContent", PageContent),
    (u"BlogEntryContent", BlogEntryContent),
    (u"LexiconEntry", LexiconEntry),
    (u"EditableHtmlHeadFile", EditableHtmlHeadFile),
    (u"DBTemplate", DBTemplate),
)
CONTENT_TYPES_CHOICES = [(no, data[0]) for no, data in enumerate(CONTENT_TYPES)]
CONTENT_TYPES_DICT = dict([(no, data[1]) for no, data in enumerate(CONTENT_TYPES)])


class FindReplaceForm(forms.Form):
    find_string = forms.CharField()
    replace_string = forms.CharField()

    content_type = forms.ChoiceField(
        choices=CONTENT_TYPES_CHOICES,
        help_text=_("Please select the content type for the operation.")
    )
    languages = forms.MultipleChoiceField(
        help_text=_("Limit the language. (Would not be used for any content type.)")
    )
    sites = forms.MultipleChoiceField(
        # choices= Set in __init__, so the Queryset would not execute at startup
        help_text=_("Limit to these sites")
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
        self.fields["languages"].initial = [Language.objects.get_current().code]

        self.fields["sites"].choices = Site.objects.all().values_list("id", "name")
        self.fields["sites"].initial = [Site.objects.get_current().id]
