# coding:utf-8

"""
    filemanager forms
    ~~~~~~~~~~~~~~~~~

    :copyleft: 2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys

import pylucid_project

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


BASE_PATHS = getattr(settings, "FILEMANAGER_BASE_PATHS",
    (
        (settings.STATIC_ROOT, settings.STATIC_URL),
        (settings.MEDIA_ROOT, settings.MEDIA_URL),
    )
)
if settings.DEBUG:
    BASE_PATHS += (
        (sys.prefix, None), # root directory of virtualenv
    )


class BasePathSelect(forms.Form):
    PATH_CHOICES = tuple([(no, path[0]) for no, path in enumerate(BASE_PATHS)])
    PATH_DICT = dict(PATH_CHOICES)
    URL_DICT = dict(tuple([(no, path[1]) for no, path in enumerate(BASE_PATHS)]))

    base_path = forms.ChoiceField(choices=PATH_CHOICES,
        help_text=_("The base path for the filemanager root directory."),
        initial=PATH_CHOICES[0],
    )

class UploadFileForm(forms.Form):
    file = forms.FileField()
