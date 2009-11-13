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


CSS_VALUE_RE = re.compile(r'[a-f0-9]{6}$', re.IGNORECASE) # For validation of a CSS value


def validate_css_color_value(value):
    """
    validate a CSS hex color value
    
    >>> validate_css_color_value("00aaff")
    >>> validate_css_color_value("00AAFF")
    
    >>> validate_css_color_value("0aF")
    Traceback (most recent call last):
    ...
    ValidationError: Error: '0aF' has wrong length (only 6 characters allowed)
    
    >>> validate_css_color_value("Maroon")
    Traceback (most recent call last):
    ...
    ValidationError: Error: 'Maroon' is not a CSS hex color value
    """
    if not isinstance(value, basestring):
        raise exceptions.ValidationError(_("CSS color value is not a basestring!"))

    if len(value) != 6:
        raise exceptions.ValidationError(
            _("Error: %r has wrong length (only 6 characters allowed)") % value
        )

    if not CSS_VALUE_RE.match(value):
        raise exceptions.ValidationError(_("Error: %r is not a CSS hex color value") % value)


#-----------------------------------------------------------------------------


class ColorValueInputWidget(forms.TextInput):
    """
    Add background-ColorValue into input tag
    
    >>> ColorValueInputWidget().render("foo", "1234af")
    u'<input style="background-ColorValue:#1234af;" type="text" name="foo" value="1234af" />'
    
    TODO: Change text ColorValue, if background is to dark ;)
    TODO2: Use jQuery to change the <td> background ColorValue ;)
    """
    def render(self, name, value, attrs=None):
        if not attrs:
            attrs = {}
        attrs["style"] = "background-ColorValue:#%s;" % value
        return super(ColorValueInputWidget, self).render(name, value, attrs)


class ColorValueFormField(forms.CharField):
    """ form field for a CSS ColorValue value """
    widget = ColorValueInputWidget
    def clean(self, value):
        """ validate the form data """
        value = super(ColorValueFormField, self).clean(value)
        validate_css_color_value(value)
        self.value = value
        return value


class ColorValueField(models.CharField):
    """
    CSS ColorValue hex value field.
    >>> ColorValueField().to_python("11AAFF")
    '11AAFF'
    
    >>> ColorValueField().to_python("0aF")
    Traceback (most recent call last):
    ...
    ValidationError: Error: '0aF' has wrong length (only 6 characters allowed)
    """
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
        kwargs['form_class'] = ColorValueFormField
        kwargs['widget'] = ColorValueInputWidget
        return super(ColorValueField, self).formfield(**kwargs)



if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
