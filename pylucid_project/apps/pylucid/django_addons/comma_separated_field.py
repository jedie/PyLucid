# coding: utf-8
"""
    django addon - comma separated field
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    TODO: FIXME ;)

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django import forms
from django.db import models


def list2string(l):
    if not l:
        return ""
    assert isinstance(l, list)
    return ", ".join([i.strip() for i in l if i])
def string2list(s):
    assert isinstance(s, basestring)
    return [i.strip() for i in s.split(",") if i]


class CommaSeparatedFormWidget(forms.TextInput):
    """ comma separated - form widget """
    def render(self, name, value, attrs=None):
        if isinstance(value, list):
            value = list2string(value)
        return super(CommaSeparatedFormWidget, self).render(name, value, attrs)


class CommaSeparatedFormField(forms.CharField):
    """ comma separated - form field """
#    widget = CommaSeparatedFormWidget
    
    def clean(self, value):
        value = super(CommaSeparatedFormField, self).clean(value)
        try:
            return string2list(value)
        except Exception, err:
            raise forms.ValidationError("Can't deserialize: %s" % err)


class CommaSeparatedCharField(models.CharField):
    """ comma separated - model field """
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, list):
            return value
        return string2list(value)

    def get_db_prep_save(self, value):
        assert isinstance(value, list)
        return list2string(value)
    
    def formfield(self, **kwargs):
        # Always use own form field and widget:
        kwargs['form_class'] = CommaSeparatedFormField
        kwargs['widget'] = CommaSeparatedFormWidget
        return super(CommaSeparatedCharField, self).formfield(**kwargs)