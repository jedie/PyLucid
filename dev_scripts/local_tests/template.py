#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A local django test with synced database but empty tables.
"""

from setup import setup
setup(
    path_info=False, extra_verbose=False,
    syncdb=True, insert_dump=True
)

#______________________________________________________________________________
# Test:

from PyLucid.models import Page, Template



print "List of all Pages:"
for page in Page.objects.all():
    print " * %s" % page
print

print "List of all Templates:"
for template in Template.objects.all():
    print " * %s" % template
print

page = Page.objects.all()[0]
template = Template.objects.get(name="basic")

from django.utils.safestring import mark_safe
page.content = mark_safe(page.content)

print template
template_content = template.content
print template_content


print "*"*79

from setup_environment import get_fake_context
context = get_fake_context(page)

from django.template import Template, Context
context2 = Context(context)
template = Template(template_content)
html = template.render(context2)
print html