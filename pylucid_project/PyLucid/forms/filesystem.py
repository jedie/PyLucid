
"""
    forms around filesystem
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    everything related to filenames, path, direcories etc.


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

from PyLucid.tools.utils import contains_char


BAD_DIR_CHARS = ("..", "//", "\\") # Bad characters in directories
BAD_FILE_CHARS = ("..", "/", "\\") # Bad characters in a filename




class BasePathField(forms.ChoiceField):
    def __init__(self, required=True, label=None, initial=None, help_text=None,
                                                             *args, **kwargs):
        
        widget = forms.Select
        choices = [(i,i) for i in settings.FILESYSTEM_BASEPATHS.keys()]
        
        super(BasePathField, self).__init__(choices, required, widget, label,
                                            initial, help_text, *args, **kwargs)
        
    def clean(self, value):
        path_key = super(BasePathField, self).clean(value)
        try:
            fs_path, url = settings.FILESYSTEM_BASEPATHS[path_key]
             
        except KeyError:
            raise forms.ValidationError("Basepath doesn't exists!")
        
        return path_key, fs_path, url
        
        

class BadCharField(forms.CharField):
    """
    A base class for DirnameField and FilenameField
    """
    def __init__(self, max_length=255, min_length=1, required=True,
                                                            *args, **kwargs):
        super(BadCharField, self).__init__(
            max_length, min_length, required, *args, **kwargs
        )

    def clean(self, value):
        """
        Check if a bad caracter is in the form value.
        """
        super(BadCharField, self).clean(value)
        if contains_char(value, self.bad_chars):
            raise forms.ValidationError(_(u"Error: Bad character found!"))

        if value.startswith("."):
            raise forms.ValidationError(_(u"Hidden name are not allowed"))

        return value

class DirnameField(BadCharField):
    """
    newforms field for verify a dirname.
    """
    bad_chars = BAD_DIR_CHARS

class FilenameField(BadCharField):
    """
    newforms field for verify a filename.
    """
    bad_chars = BAD_FILE_CHARS