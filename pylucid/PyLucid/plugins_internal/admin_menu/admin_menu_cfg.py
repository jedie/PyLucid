# -*- coding: utf-8 -*-

from pprint import pformat
from PyLucid.tools.data_eval import data_eval, DataEvalError

from django import forms
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

#_____________________________________________________________________________
# meta information
__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "Administration Menu"
__long_description__ = """"""
__can_deinstall__ = False

#_____________________________________________________________________________
# preferences

class WeightField(forms.CharField):
    def clean(self, value):
        """
        TODO: Check the data.
        """
        # Validates max_length and min_length
        value = super(WeightField, self).clean(value)

        try:
            data = data_eval(value)
        except DataEvalError, err:
            raise ValidationError("Can't evaluate data: %s" % err)

        for section_name, weight in data.iteritems():
            if not isinstance(section_name, basestring):
                raise ValidationError("Wrong section name '%r'" % section_name)
            if not isinstance(weight, int):
                raise ValidationError("Wrong weight for '%s'" % section_name)
            if weight<-10 or weight>10:
                msg = (
                    "weight for '%s' out of range (min: -10, max: 10)"
                ) % section_name
                raise ValidationError(msg)

        return data


class PreferencesForm(forms.Form):
    # TODO: Find a better way to create a better sized form
    section_weights = WeightField(
        min_length = 2,
        help_text=_(
            "Weigth for every admin sub menu section entry. (ascending order) "
        ),
        widget=forms.Textarea(attrs={'rows': '10'}),
        initial= (
            '{'
                ' "page admin": -5,'
                ' "edit look": 0,'
                ' "user management": 3,'
                ' "miscellaneous": 6,'
                ' "setup": 8,'
            '}'
        )
    )

#_____________________________________________________________________________
# plugin administration data

global_rights = {
    "must_login"    : True,
    "must_admin"    : True,
}
plugin_manager_data = {
    "lucidTag" : {
        "must_login"    : True,
        "must_admin"    : False,
        "has_Tags"      : True,
        "no_rights_error" : True, # TODO: remove in v0.9, see: ticket:161
    },
    "edit_page_link"    : global_rights,
    "new_page_link"     : global_rights,
    "del_page_link"     : global_rights,
    "sub_menu_link"     : global_rights,
    "sub_menu"          : {
        "must_login"    : True,
        "must_admin"    : False,
    },
}
