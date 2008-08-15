# -*- coding: utf-8 -*-
"""
    some utils around newforms
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django import forms
from django.forms import ValidationError
from django.utils.encoding import smart_unicode


def setup_help_text(form):
    """
    Append on every help_text the default information (The initial value)
    """
    for field_name, field in form.base_fields.iteritems():
        help_text = unicode(field.help_text) # translate gettext_lazy
        if u"(default: '" in help_text:
            # The default information was inserted in the past
            return
        field.help_text = "%s (default: '%s')" % (
            field.help_text, field.initial
        )

def get_init_dict(form):
    """
    Returns a dict with all initial values from a newforms class.
    """
    init_dict = {}
    for field_name, field in form.base_fields.iteritems():
        initial = field.initial
#        if initial == None:
#            msg = (
#                "The preferences model attribute '%s' has no initial value!"
#            ) % field_name
#            raise NoInitialError(msg)

        init_dict[field_name] = initial
    return init_dict


class NoInitialError(Exception):
    """
    All preferences newform attributes must habe a initial value.
    """
    pass


class ChoiceField2(forms.ChoiceField):
    """
    Works like a ChoiceField, but accepts a list of items. The list are
    converted to a tuple fpr rendering.
    Returns the value and not the key in clean().

    >>> f = ChoiceField2(choices=["A","B","C"])
    >>> f.choices
    [('0', u'A'), ('1', u'B'), ('2', u'C')]
    >>> f.clean('1')
    u'B'
    """
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop("choices")
        kwargs["choices"] = self.choices = [
            (str(no), smart_unicode(value)) for no, value in enumerate(choices)
        ]

        super(ChoiceField2, self).__init__(*args, **kwargs)

    def clean(self, value):
        """
        Validates that the input and returns the choiced value.
        """
        key = super(ChoiceField2, self).clean(value)
        choices_dict = dict(self.choices)
        return choices_dict[key]


class StripedCharField(forms.CharField):
    """
    Same as forms.CharField but stripes the output.

    >>> f = StripedCharField()
    >>> f.clean('\\n\\n[\\nTEST\\n]\\n\\n')
    u'[\\nTEST\\n]'
    """
    def clean(self, value):
        value = super(StripedCharField, self).clean(value)
        return value.strip()


class ListCharField(forms.CharField):
    """
    Items seperated by spaces.

    >>> f = ListCharField()
    >>> f.clean(' one two  tree')
    [u'one', u'two', u'tree']
    """
    def clean(self, value):
        raw_value = super(ListCharField, self).clean(value)
        value = raw_value.strip()
        items = [i.strip() for i in value.split(" ")]
        items = [i for i in items if i] # eliminate empty items
        return items


class InternalURLField(forms.CharField):
    """
    Uses e.g. for back urls via a http GET parameter
    validates the URL and check if is't a internal url and not
    a external.

    >>> f = InternalURLField()
    >>> f.clean('/a/foobar/url/')
    u'/a/foobar/url/'

    >>> f.clean('http://eval.domain.tld')
    Traceback (most recent call last):
        ...
    ValidationError: [u'Open redirect found.']

    >>> f = InternalURLField(must_start_with="/_command/")
    >>> f.clean('/_command/a/foobar/url/')
    u'/_command/a/foobar/url/'

    >>> f.clean('/a/wrong/url/')
    Traceback (most recent call last):
        ...
    ValidationError: [u'Open redirect found.']
    """
    default_error_message = "Open redirect found."

    def __init__(self, must_start_with=None, *args, **kwargs):
        self.must_start_with = must_start_with
        super(InternalURLField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(InternalURLField, self).clean(value)
        if "://" in value:
            raise ValidationError(self.default_error_message)
        if self.must_start_with and not value.startswith(self.must_start_with):
            raise ValidationError(self.default_error_message)
        return value



if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."