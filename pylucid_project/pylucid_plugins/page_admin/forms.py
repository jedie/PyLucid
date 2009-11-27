# coding:utf-8

from django import forms
from django.template import mark_safe
from django.forms.util import ErrorList
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext as _

from django_tools.middlewares import ThreadLocal

from pylucid_project.utils.escape import escape

from pylucid.models import PageTree, PageMeta, PageContent, PluginPage, Design, Language


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
    def clean(self):
        """ Validate if page with same slug and parent exist. """
        cleaned_data = self.cleaned_data

        if "slug" not in cleaned_data or "parent" not in cleaned_data:
            # Only do something if both fields are valid so far.
            return cleaned_data

        slug = cleaned_data["slug"]
        parent = cleaned_data["parent"]

        if parent is not None and self.instance.pk == parent.pk:
            # Check if parent is the same entry
            self._errors["parent"] = ErrorList([_("child-parent loop error!")])

        if parent and parent.page_type == parent.PLUGIN_TYPE:
            # A plugin page can't have any sub pages!
            parent_url = parent.get_absolute_url()
            msg = _(
                "Can't use the <strong>plugin</strong> page '%s' as parent page!"
                " Please choose a <strong>content</strong> page."
            ) % parent_url
            self._errors["parent"] = ErrorList([mark_safe(msg)])

        queryset = PageTree.on_site.all().filter(slug=slug, parent=parent)

        # Exclude the current object from the query if we are editing an
        # instance (as opposed to creating a new one)
        if self.instance.pk is not None:
            queryset = queryset.exclude(pk=self.instance.pk)

        exists = queryset.count()
        if exists:
            if parent == None: # parent is the tree root
                parent_url = "/"
            else:
                parent_url = parent.get_absolute_url()
            msg = "Page '%s<strong>%s</strong>/' exists already." % (parent_url, slug)
            self._errors["slug"] = ErrorList([mark_safe(msg)])

        return cleaned_data

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
        exclude = ("pagetree")


class LanguageSelectForm(forms.Form):
    language = forms.ChoiceField()

    def __init__(self, languages, *args, **kwargs):
        """ Change form field data in a DRY way """
        super(LanguageSelectForm, self).__init__(*args, **kwargs)
        self.fields['language'].choices = [(lang.code, lang.description) for lang in languages]
