# coding:utf-8

from django import forms
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from pylucid_project.apps.pylucid.models import Design, EditableHtmlHeadFile, \
                                                        ColorScheme
from django.template.loader import find_template
from django.template import TemplateDoesNotExist
from django.core.urlresolvers import reverse, NoReverseMatch




class SelectDesignBaseForm(forms.Form):
    """
    Select a exsiting design. Used in "switch design" and "clone design"
    """
    design = forms.ChoiceField(
        # choices= Set in __init__, so the Queryset would not execute at startup
        required=False, initial=None,
        help_text=_("Select the PyLucid page design")
    )

    def __init__(self, *args, **kwargs):
        super(SelectDesignBaseForm, self).__init__(*args, **kwargs)

        designs = Design.on_site.all().values_list("id", "name")
        self.fields["design"].choices = list(designs)


class SwitchDesignForm(SelectDesignBaseForm):
    def __init__(self, *args, **kwargs):
        super(SwitchDesignForm, self).__init__(*args, **kwargs)
        self.fields["design"].choices.insert(0, (0, "<automatic>"))



class CloneDesignForm(SelectDesignBaseForm):
    new_name = forms.CharField(
        help_text=_("Name of the cloned design. (used for all design components, too)")
    )
    sites = forms.MultipleChoiceField(
        # choices= Set in __init__, so the Queryset would not execute at startup
        help_text=_("Site set to all design components")
    )

    def __init__(self, *args, **kwargs):
        super(CloneDesignForm, self).__init__(*args, **kwargs)
        self.fields["sites"].choices = Site.objects.all().values_list("id", "name")
        self.fields["sites"].initial = [Site.objects.get_current().id]

    def get_new_template_name(self):
        new_name = self.cleaned_data["new_name"]
        return "%s.html" % new_name

    def clean_new_name(self):
        new_name = self.cleaned_data["new_name"]
        new_name = new_name.strip()

        try: # "validate" with the url re FIXME: Do it better ;) 
            reverse('PyLucid-send_head_file', kwargs={"filepath": new_name})
        except NoReverseMatch, err:
            raise forms.ValidationError(_(
                "new name contains invalid characters!"
                " (Original error: %s)" % err,
            ))

        if Design.objects.filter(name__iexact=new_name).count() != 0:
            raise forms.ValidationError(_("A design with this name exist already."))

        if ColorScheme.objects.filter(name__iexact=new_name).count() != 0:
            raise forms.ValidationError(_("A ColorScheme with this name exist already."))

        if EditableHtmlHeadFile.objects.filter(filepath__istartswith=new_name).count() != 0:
            raise forms.ValidationError(_("A editable headfile filepath startswith with this new name."))

        template_name = self.get_new_template_name()
        try:
            find_template(template_name)
        except TemplateDoesNotExist, err:
            pass
        else:
            raise forms.ValidationError(_("A template named '%s' exist already") % template_name)

        return new_name


