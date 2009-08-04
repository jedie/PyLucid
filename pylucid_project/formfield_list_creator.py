#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    dev script
"""

import os

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

from django_tools.template import render

ENTITIES = {
    "&#x7B;": "{",
    "&#x7D;": "}",
}
"""
        &#x7B;% if field.field.required %}<strong>{{ field.label }}</strong>&#x7B;% else %}{{ field.label }}&#x7B;% endif %}
        :       
        &#x7B;% if field.errors %}
            &#x7B;% for error in field.errors %}{{ error|escape }}&#x7B;% endfor %}
        &#x7B;% endif %}
        </label>
"""
TEMPLATE = u"""{% for field in form %}
&#x7B;% with form.{{ field.html_name }} as field %&#x7D;
    &#x7B;% include "admin/pylucid/includes/form_field.html" %&#x7D;
&#x7B;% endwith %&#x7D;
{% endfor %}"""


#______________________________________________________________________________
# Test app code:

from pylucid_plugins.page_admin.forms import PageContentForm, PluginPageForm


#------------------------------------------------------------------------------
if __name__ == "__main__":
    form = PluginPageForm()
    context = {
        "form": form,
    }
    output = render.render_string_template(TEMPLATE, context)
    for k, v in ENTITIES.items():
        output = output.replace(k, v)
    print output

#    for field in form:
#        print field
#        print "-" * 79
#    print f

    print "-" * 80
    print "- END -"
