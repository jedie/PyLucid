# coding:utf-8

from django import forms
from django.utils.translation import ugettext_lazy as _

from pylucid_project.apps.pylucid.models import Design


class SelectDesign(forms.Form):
    design = forms.ChoiceField(
        # choices= Set in __init__, so the Queryset would not execute at startup
        required=False, initial=None,
        help_text=_("Select the PyLucid page design")
    )

    def __init__(self, *args, **kwargs):
        super(SelectDesign, self).__init__(*args, **kwargs)
        designs = Design.on_site.all().values_list("id", "name")
        self.fields["design"].choices = [(0, "<automatic>")] + list(designs)
