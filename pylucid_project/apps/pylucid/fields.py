# coding: utf-8

"""
    PyLucid fields
    ~~~~~~~~~~~~~~

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import re

if __name__ == "__main__":
    # For doctest only
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"

from django import forms
from django.db import models
from django.core import exceptions
from django.utils.translation import ugettext as _

from south.modelsinspector import add_introspection_rules

from pylucid_project.apps.pylucid.markup.widgets import MarkupContentWidget, \
    MarkupSelectWidget
from pylucid_project.apps.pylucid.markup import MARKUP_CHOICES

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

    def get_db_prep_save(self, value, connection):
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


#______________________________________________________________________________
# Markup


class MarkupContentModelField(models.TextField):
    def formfield(self, **kwargs):
        # Use our own widget and put JavaScript preview stuff into page.
        kwargs['widget'] = MarkupContentWidget()
        return super(MarkupContentModelField, self).formfield(**kwargs)

add_introspection_rules([], ["^pylucid_project\.apps\.pylucid\.fields\.MarkupContentModelField"])


class MarkupModelField(models.PositiveSmallIntegerField):
    # TODO: update in next migration release. Original was: models.IntegerField
    def __init__(self, *args, **kwargs):
        defaults = {
            "choices": MARKUP_CHOICES,
            "help_text": _("the used markup language for this entry"),
        }
        defaults.update(kwargs)
        super(MarkupModelField, self).__init__(*args, **defaults)

    def formfield(self, **kwargs):
        # Use our own widget to put markup select field id into a JavaScript variable
        kwargs['widget'] = MarkupSelectWidget()
        return super(MarkupModelField, self).formfield(**kwargs)

add_introspection_rules([], ["^pylucid_project\.apps\.pylucid\.fields\.MarkupModelField"])


class RootAppChoiceField(models.CharField):
    def get_choices_default(self):
        from pylucid_project.apps.pylucid.models.pluginpage import PluginPage # import loops
        PluginPage.objects.get_app_choices()


try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules([], ["^pylucid_project\.apps\.pylucid\.fields.\ColorValueFormField"])
    add_introspection_rules([], ["^pylucid_project\.apps\.pylucid\.fields.\ColorValueField"])
    add_introspection_rules([], ["^pylucid_project\.apps\.pylucid\.fields.\MarkupContentModelField"])
    add_introspection_rules([], ["^pylucid_project\.apps\.pylucid\.fields.\MarkupModelField"])
    add_introspection_rules([], ["^pylucid_project\.apps\.pylucid\.fields.\RootAppChoiceField"])


if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
