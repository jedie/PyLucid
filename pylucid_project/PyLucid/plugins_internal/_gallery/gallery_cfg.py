# -*- coding: utf-8 -*-

#_____________________________________________________________________________
# meta information
__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = \
"File/Picture gallery (NOT USEABLE! UNDER CONSTRUCTION!)"
__long_description__ = """
A universal file/picture gallery plugin.
"""

from django import forms
from django.utils.translation import ugettext as _

from django.conf import settings

#______________________________________________________________________________
# Build a list and a dict from the basepaths
# The dict key is a string, not a integer. (GET/POST Data always returned
# numbers as strings)

BASE_PATHS = [
    (str(no),unicode(path)) for no,path in enumerate(settings.FILEMANAGER_BASEPATHS)
]
BASE_PATHS_DICT = dict(BASE_PATHS)

#_____________________________________________________________________________
# preferences


class PreferencesForm(forms.Form):
    """
    Default settings for a new gallery.
    Every gallery can have differend settings. These default values only used
    if a new gallery would be created. After this you can edit the individual
    gallery settings in the gallery themself.
    """
    base_path = forms.ChoiceField(choices=BASE_PATHS,
        help_text = _(
            "Index directory of the gallery."
            " You can select a path from settings.FILEMANAGER_BASEPATHS"
        ),
    )

    ext_whitelist = forms.CharField(
        initial = ".jpg, .png, .mpg, .avi",
        help_text = _("Witch filetypes should be included in the gallery?"),
    )

    dir_filter = forms.CharField(
        initial = "", required=False,
        help_text = _("Comma seperated list of direcories to skip."),
    )
    file_filter = forms.CharField(
        initial = "", required=False,
        help_text = _("Comma seperated list of files to skip."),
    )

    allow_subdirs = forms.BooleanField(
        initial = True,
        help_text = _(
            "include sub directories or hide them?"
        ),
    )

    pic_ext = forms.CharField(
        initial = ".jpg, .jpeg",
        help_text = _(
            "filetypes how displays as pictures and not as normal files?"
        ),
    )
    thumb_pic_filter = forms.CharField(
        initial = "_WEB,_FULL,_BIG",
        help_text = _(
            "filename suffix for the pictures."
            " (comma seperated list, spaces recognized!)"
        ),
    )
    thumb_suffix = forms.CharField(
        initial = "_thumb,_small",
        help_text = _(
            "filename suffix for a thumbnail picture?"
            " (comma seperated list, spaces recognized!)"
        ),
    )

    default_thumb_width = forms.IntegerField(
        initial = 100,
        min_value = 10,
        help_text = _(
            "Default thumbnail width"
            " (Scale picture, if no thumbnail exist)."
        ),
    )
    default_thumb_height = forms.IntegerField(
        initial = 60,
        min_value = 10,
        help_text = _(
            "Default thumbnail height"
            " (Scale original picture, if no thumbnail exist)."
        ),
    )

    robots = forms.CharField(
        initial = "",
        help_text = _(
            "html meta information (e.g.: 'noindex,nofollow')"
            " (If empty, used the default template robots entry)"
        ),
        #required = False #???
    )

    verbose_level = forms.IntegerField(
        initial = 0, min_value = 0, max_value = 3,
        help_text = _(
            "Display debug information (Only if a admin is logged in!)?"
        ),
    )



#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
    "lucidTag" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
    "admin": {
        "must_login": True,
        "must_admin": False,
        "admin_sub_menu": {
            "section"       : _("multimedia"), # The sub menu section
            "title"         : _("gallery"),
            "help_text"     : _("Administrate the galleries."),
            "open_in_window": False, # Should be create a new JavaScript window?
            "weight" : 0, # sorting wieght for every section entry
        },

    },
}
