# coding:utf-8

from django import forms
from django.template import mark_safe
from django.forms.util import ErrorList
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext as _

from django_tools.middlewares import ThreadLocal

from pylucid.models import PageTree, PageMeta, PageContent, PluginPage, Design, Language


class EditPageForm(forms.Form):
    """
    Form for "quick inline" edit.
    """
    edit_comment = forms.CharField(
        max_length=255, required=False,
        help_text=_("The reason for editing."),
        widget=forms.TextInput(attrs={'class':'bigger'}),
    )

    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': '15'}),
    )



class AboluteUrlChoiceField(forms.ModelChoiceField):
    """
    FIXME: The root page order is wrong!
    """
    def __iter__(self):
        if self.empty_label is not None:
            yield (u"", self.empty_label)

        for item in sorted(self.queryset.all(), key=lambda i: i.get_absolute_url()):
            yield (item.pk, item.get_absolute_url())

    def _get_choices(self):
        return self

    choices = property(_get_choices, forms.ChoiceField._set_choices)


class BasePageForm(forms.ModelForm):
    """ Base form class for PageContentForm and PluginPageForm. """
    # TODO: Use TreeGenerator for parent field!
    parent = AboluteUrlChoiceField(queryset=PageTree.on_site, label=_('Parent'), help_text=_('the higher-ranking father page'), required=False)
    def clean(self):
        """ Validate if page with same slug and parent exist. """
        cleaned_data = self.cleaned_data

        if "slug" not in cleaned_data or "parent" not in cleaned_data:
            # Only do something if both fields are valid so far.
            return cleaned_data

        slug = cleaned_data["slug"]
        parent = cleaned_data["parent"]
        exists = PageTree.on_site.all().filter(slug=slug, parent=parent).count()
        if exists:
            if parent == None: # parent is the tree root
                parent_url = "/"
            else:
                parent_url = parent.get_absolute_url()
            msg = "Page '%s<strong>%s</strong>/' exists already." % (parent_url, slug)
            self._errors["slug"] = ErrorList([mark_safe(msg)])

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(BasePageForm, self).__init__(*args, **kwargs)

        # Change field in a DRY way
        self.fields['design'].choices = Design.on_site.values_list("id", "name")



class PageContentModel(PageTree, PageMeta, PageContent):
    """ merged model for PageContentForm """
    class Meta:
        #managed = False
        abstract = True

class PageContentForm(BasePageForm):
    class Meta:
        model = PageContentModel
        exclude = ("page", "pagemeta", "page_type", "site", "lang")


class PluginPageModel(PageTree, PageMeta, PluginPage):
    """ merged model for PluginPageForm """
    class Meta:
        #managed = False
        abstract = True

class PluginPageForm(BasePageForm):
    """
    TODO: 
    """
    app_label = forms.TypedChoiceField(choices=PluginPage.objects.get_app_choices(), label=_('App label'), help_text=_('The app lable witch is in settings.INSTALLED_APPS'))
    urls_filename = forms.CharField(label=_('Urls filename'), initial=_('urls.py'), help_text=_('Filename of the urls.py'))
    class Meta:
        model = PluginPageModel
        exclude = ("page", "pagemeta", "page_type", "site")
