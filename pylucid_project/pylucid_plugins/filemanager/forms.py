# coding:utf-8

"""
    filemanager forms
    ~~~~~~~~~~~~~~~~~

    :copyleft: 2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import sys

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


# The base path for the filemanager. Every path is like:
BASE_PATHS = getattr(settings, "FILEMANAGER_BASE_PATHS",
    (
        {
            # The absolute filesystem root direcotry:
            "abs_base_path": settings.STATIC_ROOT,
            # The url prefix for the files, if exists:
            "url_prefix": settings.STATIC_URL,
            # File upload to every sub path are allowed:
            "allow_upload": True,
        },
        {
            "abs_base_path": settings.MEDIA_ROOT,
            "url_prefix": settings.MEDIA_URL,
            "allow_upload": True,
        },
    )
)
if settings.DEBUG:
    BASE_PATHS += (
        {
            "abs_base_path": sys.prefix, # root directory of virtualenv
            "url_prefix": None,
            "allow_upload": False,
        },

    )


class BasePathSelect(forms.Form):
    PATH_CHOICES = tuple([(no, path["abs_base_path"]) for no, path in enumerate(BASE_PATHS)])
    PATH_DICT = dict(tuple([(no, path) for no, path in enumerate(BASE_PATHS)]))

    base_path = forms.ChoiceField(choices=PATH_CHOICES,
        help_text=_("The base path for the filemanager root directory."),
        initial=PATH_CHOICES[0],
    )

class UploadFileForm(forms.Form):
    file = forms.FileField()
