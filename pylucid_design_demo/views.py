# coding: utf-8

"""
    PyLucid DesignSwitch Plugin
    ~~~~~~~~~~~~~~~~~~~

    :copyleft: 2015-2016 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib import messages

from cms.models import Page

EXISTING_TEMPLATES = [t[0] for t in settings.CMS_TEMPLATES]

def switch_template(request, page_id, template):
    assert template in EXISTING_TEMPLATES
    current_page = Page.objects.get(pk=int(page_id))

    Page.objects.all().update(template=template)
    messages.info(request, "Set template %r to all pages, ok." % template)

    redirect_url = current_page.get_absolute_url()
    redirect_url += "?edit_off" # always view the published page
    return HttpResponseRedirect(redirect_url)