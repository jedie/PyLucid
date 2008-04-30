#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A local django test with synced database but empty tables.
"""

from setup import setup
setup(
    path_info=False, extra_verbose=False,
    syncdb=False, insert_dump=False
)

#______________________________________________________________________________
# Test:

from django import newforms as forms

class SearchPreferences(forms.Form):
    min_term_len = forms.IntegerField(
        help_text="Min length of a search term",
        initial=3, min_value=1
    )
    max_term_len = forms.IntegerField(
        help_text="Max length of a search term",
        initial=50, min_value=1, max_value=200
    )


def test(form):
#    print form
#    for i in dir(form):
#        print i, getattr(form, i, "---")
        
    for field_name, field in form.base_fields.iteritems():
        field.help_text = "%s (default: '%s')" % (
            field.help_text, field.initial
        )
        
    return form()

def setup_help_text(form):
    for field_name, field in form.base_fields.iteritems():
        field.help_text = "%s (default: '%s')" % (
            field.help_text, field.initial
        )


p = test(SearchPreferences)
#p = SearchPreferences()
#setup_help_text(p)
print p.as_p().replace(">", ">\n")


print " - END -"