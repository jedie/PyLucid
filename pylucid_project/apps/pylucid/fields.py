# coding:utf-8

import re

if __name__ == "__main__":
    # For doctest only
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"

from django import forms
from django.db import models
from django.core import exceptions
from django.utils.translation import ugettext as _



CSS_VALUE_RE = re.compile(r'[a-fA-F0-9]{3,6}$') # For validation of a CSS value


def validate_css_color_value(value):
    """
    validate a CSS hex color value
    
    >>> validate_css_color_value("00aaff")
    >>> validate_css_color_value("00AAFF")
    >>> validate_css_color_value("0af")
    >>> validate_css_color_value("0AF")
    
    >>> validate_css_color_value("")
    Traceback (most recent call last):
    ...
    ValidationError: Wrong CSS color length (only 3 or 6 characters)
    
    >>> validate_css_color_value("Maroon")
    Traceback (most recent call last):
    ...
    ValidationError: Error: 'Maroon' is not a CSS hex color value
    """
    if not isinstance(value, basestring):
        raise exceptions.ValidationError(_("CSS color value is not a basestring!"))
    
    if len(value) not in (3, 6):
        raise exceptions.ValidationError(_("Wrong CSS color length (only 3 or 6 characters)"))
    
    if not CSS_VALUE_RE.match(value):
        raise exceptions.ValidationError(_("Error: %r is not a CSS hex color value") % value)


class ColorFormField(forms.CharField):
    """ form field for a CSS color value """
#    widget = DictFormWidget
    def clean(self, value):
        """ validate the form data """
        value = super(ColorFormField, self).clean(value)
        validate_css_color_value(value)
        return value


class ColorField(models.CharField):
    """ CSS color hex value field. """
    #__metaclass__ = models.SubfieldBase
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 6
        models.CharField.__init__(self, *args, **kwargs)

    def get_db_prep_save(self, value):
        "Returns field's value prepared for saving into a database."
        validate_css_color_value(value)
        return value

    def to_python(self, value):
        validate_css_color_value(value)
        return value

    def formfield(self, **kwargs):
        # Always use own form field and widget:
        kwargs['form_class'] = ColorFormField
        return super(ColorField, self).formfield(**kwargs)



if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."