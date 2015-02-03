# coding:utf-8

from django import forms
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext as _

from blog.models import BlogEntry
from lexicon.models import LexiconEntry
from update_journal.models import UpdateJournal
from pylucid_comments.models import PyLucidComment

from pylucid_project.apps.pylucid.markup import MARKUP_CHOICES, MARKUP_CREOLE, \
    MARKUP_HTML, MARKUP_HTML_EDITOR
from pylucid_project.apps.pylucid.models import PageTree, PageMeta, PageContent, PluginPage, \
                                                                            Design, Language
from pylucid_project.utils.escape import escape


class PageContentTextarea(forms.Textarea):
    def __init__(self):
        # The 'rows' and 'cols' attributes are required for HTML correctness.
        self.attrs = {'cols': '40', 'rows': '15'}

    def render(self, name, value, attrs=None):
        if value:
            value = escape(value)
        return super(PageContentTextarea, self).render(name, value, attrs)


class EditPageForm(forms.Form):
    """ Form for "quick inline" edit. """
    content = forms.CharField(widget=PageContentTextarea())


class PageTreeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        """ Change form field data in a DRY way """
        super(PageTreeForm, self).__init__(*args, **kwargs)
        designs = Design.on_site.values_list("id", "name")
        self.fields['design'].choices = [("", "---------")] + list(designs)

        if self.instance:
            # Filter the own entry from parent choices list -> prevent parent-child loops
            exclude_extras = {"pk": self.instance.pk}
        else:
            exclude_extras = None

        self.fields["parent"].widget = forms.widgets.Select(
            choices=PageTree.objects.get_choices(exclude_extras=exclude_extras)
        )

    class Meta:
        model = PageTree
        exclude = ("page_type", "site")


class PageMetaForm(forms.ModelForm):
    class Meta:
        model = PageMeta
        exclude = ("pagetree", "language")


class PageContentForm(forms.ModelForm):
    class Meta:
        model = PageContent
        exclude = ("pagemeta",)

def _markup_choices(*id_filter):
    choices = [entry for entry in MARKUP_CHOICES if entry[0] in id_filter]
    return choices


class ConvertMarkupForm(forms.ModelForm):
    # Use only supported markups for converting choice field
    MARKUP_CHOICES2 = _markup_choices(
        MARKUP_CREOLE, MARKUP_HTML, MARKUP_HTML_EDITOR
    )
    dest_markup = forms.ChoiceField(
        choices=MARKUP_CHOICES2,
        help_text=_("convert the current page content to this new markup"),
    )
    verbose = forms.BooleanField(required=False,
        help_text=_("Display original html and a html diff."),
    )
    def clean_markup(self):
        return int(self.cleaned_data['markup'])
    class Meta:
        model = PageContent
        fields = ('content',)


class SelectMarkupForm(forms.Form):
    """ for page list admin view """
    markup_id = forms.ChoiceField(
        choices=MARKUP_CHOICES,
        help_text=_("switch to other markup format"),
    )
    def clean_markup_id(self):
        return int(self.cleaned_data['markup_id'])


class PluginPageForm(forms.ModelForm):
#    app_label = forms.TypedChoiceField(
#        choices=PluginPage.objects.get_app_choices(), label=_('App label'),
#        help_text=_('The app lable witch is in settings.INSTALLED_APPS')
#    )
    def __init__(self, *args, **kwargs):
        """ Change form field data in a DRY way """
        super(PluginPageForm, self).__init__(*args, **kwargs)
        self.fields["app_label"].widget = forms.widgets.Select(choices=PluginPage.objects.get_app_choices())

    class Meta:
        model = PluginPage
        # https://docs.djangoproject.com/en/1.6/releases/1.6/#modelform-without-fields-or-exclude
        # exclude = ("pagetree")


class PageOderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        """ Change form field data in a DRY way """
        super(PageOderForm, self).__init__(*args, **kwargs)
        choices = [(i, i) for i in range(-10, 10)]
        for field_name, field in self.fields.iteritems():
            field.widget = forms.widgets.Select(choices=choices)

    class Meta:
        model = PageTree

PageOrderFormSet = modelformset_factory(
    model=PageTree, form=PageOderForm, extra=0, fields=('position',)
)


class MassesEditorSelectForm(forms.Form):
    """
    TODO: implement a API for generating _DATA. So that other plugins can easy add some items.
    """
    _DATA = (
        (PageTree, False, "slug", "parent", "design", "showlinks", "permitViewGroup", "permitEditGroup"),
        (PageMeta, True, "name", "title", "tags", "keywords", "robots", "permitViewGroup"),
        (BlogEntry, True, "tags", "is_public"),
        (LexiconEntry, True, "tags", "alias", "short_definition", "is_public"),
        (UpdateJournal, True, "staff_only"),
        (PyLucidComment, False, "notify", "is_public", "is_removed"),
    )
    CHOICES = [] # Used by the model_attr field
    _CHOICES_DICT = {} # Used in self.clean_model_attr()
    id = 0
    for model_data in _DATA:
        for attr in model_data[2:]:
            id += 1
            CHOICES.append((id, "%s.%s" % (model_data[0].__name__, attr)))
            _CHOICES_DICT[id] = (model_data[0], model_data[1], attr)

    model_attr = forms.ChoiceField(choices=CHOICES,
        label="model attribute", help_text=_("The model and attribute for bulk edit.")
    )
    language = forms.ModelChoiceField(queryset=Language.on_site.all(), empty_label=None,
        help_text=_("Filter queryset in this language (if possible)")
    )

    def hide_all_fields(self):
        """ hide all fields (assign HiddenInput widget """
        for field_name, field in self.fields.iteritems():
            field.widget = forms.widgets.HiddenInput()

    def clean_model_attr(self):
        """ Don't return only the internal ID -> return (model, filter_lang, attr) """
        id = int(self.cleaned_data['model_attr'])
        return self._CHOICES_DICT[id]

