# coding:utf-8

from django import forms
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext as _

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


class PageContentModel(PageTree, PageMeta, PageContent):
    """ merged model for PageContentForm """
    class Meta:
        #managed = False
        abstract = True

class PageContentForm(BasePageForm):
    class Meta:
        model = PageContentModel
        exclude = ('page', "pagemeta", "page_type")


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
        exclude = ('page', "pagemeta", "page_type")
