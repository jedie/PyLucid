# -*- coding: UTF-8 -*-
"""
    some utils around newforms
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

def setup_help_text(form):
    """
    Append on every help_text the default information (The initial value)
    """
    for field_name, field in form.base_fields.iteritems():
        if "(default: '" in field.help_text:
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
        if initial == None:
            msg = (
                "The preferences model attribute '%s' has no initial value!"
            ) % field_name
            raise NoInitialError(msg)

        init_dict[field_name] = initial
    return init_dict


class NoInitialError(Exception):
    """
    All preferences newform attributes must habe a initial value.
    """
    pass