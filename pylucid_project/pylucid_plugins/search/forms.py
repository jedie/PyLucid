# coding:utf-8

from django import forms

from pylucid_project.pylucid_plugins.search.preference_forms import get_preferences
from pylucid_project.apps.pylucid.models.language import Language

class SearchForm(forms.Form):
    search = forms.CharField(widget=forms.TextInput(
        attrs={
            "required":"required",
            "autofocus":"autofocus",

        }
    ))
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

        preferences = get_preferences()
        self.fields['search'].min_length = preferences["min_term_len"]
        self.fields['search'].max_length = preferences["max_term_len"]


class AdvancedSearchForm(SearchForm):
    language = forms.MultipleChoiceField(
        choices=Language.objects.get_choices(),
        widget=forms.CheckboxSelectMultiple,
    )
