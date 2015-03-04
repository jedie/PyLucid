# coding: utf-8

"""
    PyLucid DesignSwitch Plugin
    ~~~~~~~~~~~~~~~~~~~

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings
from django.http import HttpResponseRedirect

from cms.models import Page
from cms.utils import get_language_from_request


EXISTING_TEMPLATES = [t[0] for t in settings.CMS_TEMPLATES]


def switch_template(request, page_id, template):
    assert template in EXISTING_TEMPLATES
    current_page = Page.objects.get(pk=int(page_id))

    root_page = Page.objects.get_home()
    if root_page.template != template:
        # print("Save %r to %r" % (template, root_page.get_absolute_url()))
        root_page.template = template
        root_page.save()

        if settings.USE_I18N:
            language = get_language_from_request(request)
        else:
            language = settings.LANGUAGE_CODE

        root_page.publish(language=language)

    redirect_url = current_page.get_absolute_url()
    return HttpResponseRedirect(redirect_url)