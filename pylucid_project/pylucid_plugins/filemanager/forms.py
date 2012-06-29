# coding:utf-8

"""
    filemanager forms
    ~~~~~~~~~~~~~~~~~

    :copyleft: 2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

BASE_PATHS = getattr(settings, "FILEMANAGER_BASE_PATHS",
    (settings.STATIC_ROOT, settings.MEDIA_ROOT)
)


class BasePathSelect(forms.Form):
    PATH_CHOICES = tuple([(no, path) for no, path in enumerate(BASE_PATHS)])
    PATH_DICT = dict(PATH_CHOICES)

    base_path = forms.ChoiceField(choices=PATH_CHOICES,
        help_text=_("The base path for the filemanager root directory."),
        initial=PATH_CHOICES[0],
    )
