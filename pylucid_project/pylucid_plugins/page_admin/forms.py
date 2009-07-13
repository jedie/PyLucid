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


#class PageTreeForm(forms.ModelForm):
#    class Meta:
#        model = PageTree
#        exclude = ("site",)
#
#class PageContentForm(forms.ModelForm):
#    class Meta:
#        model = PageContent
#        exclude = ("page", "pagemeta")
#
#class PageMetaForm(forms.ModelForm):
#    class Meta:
#        model = PageMeta
#        exclude = ("page", "lang")
#
#class PageForm(PageTreeForm, PageContentForm, PageMetaForm):
#    pass

class BasePageForm(forms.Form):
    """
    Base form class for PageContentForm and PluginPageForm.
    All fields for PageTree and PageMeta models.
    """
    parent = AboluteUrlChoiceField(queryset=PageTree.objects.all(), label=_('Parent'), initial=None, help_text=_('the higher-ranking father page'), required=False)
    position = forms.IntegerField(label=_('Position'), initial=0, help_text=_('ordering weight for sorting the pages in the menu.'))

    design = forms.ModelChoiceField(queryset=Design.objects.all(), label=_('Design'), initial=None, help_text=_('Page Template, CSS/JS files'))
    showlinks = forms.BooleanField(label=_('Showlinks'), initial=True, help_text=_('Put the Link to this page into Menu/Sitemap etc.?'), required=False)
    permitViewGroup = forms.ModelChoiceField(queryset=Group.objects.all(), label=_('PermitViewGroup'), initial=None, help_text=_('Limit viewable to a group?'), required=False)
    permitEditGroup = forms.ModelChoiceField(queryset=Group.objects.all(), label=_('PermitEditGroup'), initial=None, help_text=_('Usergroup how can edit this page.'), required=False)

    name = forms.CharField(label=_('Name'), initial=None, help_text=_('Sort page name (for link text in e.g. menu)'), required=False)
    slug = forms.SlugField(label=_('Slug'), initial=None, help_text=_('(for building URLs)'))
    title = forms.CharField(label=_('Title'), initial=None, help_text=_('A long page title (for e.g. page title or link title text)'), required=False)

    lang = forms.ModelChoiceField(queryset=Language.objects.all(), label=_('Language'), initial=None)

    keywords = forms.CharField(label=_('Keywords'), initial=None, help_text=_('Keywords for the html header. (separated by commas)'), required=False)
    description = forms.CharField(label=_('Description'), initial=None, help_text=_('For html header'), required=False)
    robots = forms.CharField(label=_('Robots'), initial='index,follow', help_text=_("for html 'robots' meta content."))
    permitViewGroup = forms.ModelChoiceField(queryset=Group.objects.all(), label=_('PermitViewGroup'), initial=None, help_text=_('Limit viewable to a group?'), required=False)

class PageContentForm(BasePageForm):
    """
    Form for creating a new content page.
    TODO: Find a DRY way to get the fields directly from the PageTree, PageContent and PageMeta models.
    """
    content = forms.CharField(
        label=_('Content'), initial=None, help_text=_('The CMS page content.'), required=False,
        widget=forms.Textarea(attrs={'rows': '15'}),
    )
    markup = forms.TypedChoiceField(choices=PageContent.MARKUP_CHOICES, label=_('Markup'), initial=None)


class PluginPageForm(BasePageForm):
    """
    Form for creating a new plugin page.
    TODO: Find a DRY way to get the fields directly from the PageTree, PagePlugin and PageMeta models.
    """
    app_label = forms.TypedChoiceField(choices=PluginPage.objects.get_app_choices(), label=_('App label'), initial=None, help_text=_('The app lable witch is in settings.INSTALLED_APPS'))
    urls_filename = forms.CharField(label=_('Urls filename'), initial=_('urls.py'), help_text=_('Filename of the urls.py'))

