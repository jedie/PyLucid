# coding: utf-8

"""
    PyLucid
    ~~~~~~~

    :copyleft: 2009-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from django.contrib import admin
from django.core import serializers
from django.http import HttpResponse

from cms.models import Page

from reversion_compare.helpers import patch_admin


logger = logging.getLogger(__name__)


# Patch django-cms Page Model to add reversion-compare functionality:
patch_admin(Page)


def export_as_json(modeladmin, request, queryset):
    """
    from:
    http://docs.djangoproject.com/en/dev/ref/contrib/admin/actions/#actions-that-provide-intermediate-pages
    """
    response = HttpResponse(content_type="text/javascript")
    serializers.serialize("json", queryset, stream=response, indent=4)
    return response

# Make export actions available site-wide
admin.site.add_action(export_as_json, 'export_selected_as_json')

