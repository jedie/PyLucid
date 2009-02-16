# -*- coding: utf-8 -*-

"""
    PyLucid Base Filesystem Plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    A base plugin for stuff like Filemanager, Gallery

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

from django import forms
from django.http import Http404, HttpResponseRedirect
from django.conf import settings
from django.utils.translation import ugettext as _

from PyLucid.tools.utils import contains_char
from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.forms.filesystem import FilenameField, DirnameField, \
                                BasePathField, BAD_DIR_CHARS, BAD_FILE_CHARS 

#______________________________________________________________________________


class SelectBasePathForm(forms.Form):
    """ change the base path form """
    base_path = BasePathField()


#______________________________________________________________________________

class Path(dict):
    """
    Helper class for analyse, check and store the html GET path information.
    Used in filemanager()

    base_key       = BASE_PATHS_DICT key (Note: it's a String!)
    base_path     = relative base path
    abs_base_path = absolute filesystem base path
    rel_path      = relative path (from GET)
    abs_path      = absolute filesystem path (abs_base_path + rel_path)
    url_path      = base_key + rel_path for html links

    - only with new_filename_path():
    filename      = contains only the filename
    abs_file_path = absolute filesystem path incl. filename
    """
    def __init__(self, context):
        self.context     = context
        self.request     = context["request"]
        self.page_msg    = self.request.page_msg

    def new_dir_path(self, path_info, must_exist=True):
        """
        split the html-GET path information and build the absolute filesystem
        path.
        if must_exist==True: The given path must allready exists.
        
        base_dict is a dict =BASE_PATHS_DICT
        
        """
        if contains_char(path_info, BAD_DIR_CHARS):
            raise Http404(_(u"Error: Bad character found!"))

        path_info = os.path.normpath(path_info)
        path_info2 = path_info.split("/", 1)

        if len(path_info2) == 1:
            # e.g. edit a file in the base_path root
            base_key = path_info
            rel_path = ""
        else:
            try:
                base_key, rel_path = path_info2
            except ValueError:
                if self.request.debug:
                    raise
                raise Http404(_("Wrong path!"))

        try:
            base_fs_path, base_url = settings.FILESYSTEM_BASEPATHS[base_key]
        except KeyError:
            raise Http404(_("Wrong basepath!"))

        base_fs_path = os.path.normpath(base_fs_path)
        abs_base_path = os.path.abspath(base_fs_path)

        abs_path = os.path.normpath(os.path.join(abs_base_path, rel_path))
        if must_exist and not os.path.exists(abs_path):
            raise Http404(_("Error: Path '%s' doesn't exist.") % abs_path)

        self["base_key"] = base_key
        self["base_fs_path"] = base_fs_path
        self["base_url"] = base_url
        
        self["abs_base_path"] = abs_base_path
        self["rel_path"] = rel_path
        self["abs_path"] = abs_path
        self["url_path"] = os.path.normpath(os.path.join(base_key, rel_path))


    def new_filename_path(self, file_path, must_exist=True):
        """
        Split a html GET path information witch contains a filename.
        if must_exist==True: The file must exist in the given path.
        """
        path_info, filename = os.path.split(file_path)

        self.new_dir_path(path_info, must_exist)

        if contains_char(filename, BAD_FILE_CHARS):
            raise Http404(_(u"Error: Bad character found!"))

        abs_file_path = os.path.join(self["abs_path"], filename)

        if must_exist and not os.path.isfile(abs_file_path):
            raise Http404(_("Error: File '%s' doesn't exist.") % filename)

        self["filename"] = filename
        self["abs_file_path"] = abs_file_path

    #--------------------------------------------------------------------------

    def get_abs_link(self, item=""):
        """
        returns a absolute link to the given item.
        """
        return os.path.join("/", self["base_url"], self["rel_path"], item)

    
    #--------------------------------------------------------------------------

    def debug(self):
        """
        write debug information into the page_msg
        """
        self.page_msg("path debug:")
        for k,v in self.items():
            self.page_msg(" - %15s: '%s'" % (k,v))



#______________________________________________________________________________



class FilesystemPlugin(PyLucidBasePlugin):
    def __init__(self, context, response, plugin_name):
        super(FilesystemPlugin, self).__init__(context, response, plugin_name)
        self.path = Path(context)
        
    #--------------------------------------------------------------------------
    
    def basepath_form(self, context):
        """
        add a form for selecting a base path from settings.FILESYSTEM_BASEPATHS
        into the context (key: "select_basepath")
        
        After a valide POST we return the 'path_key'.
        """
        if self.request.method == 'POST':
            form = SelectBasePathForm(self.request.POST)
            if form.is_valid():
                path_key, fs_path, url = form.cleaned_data["base_path"]
                if not os.path.isdir(fs_path):
                    if self.request.debug:
                        path = fs_path
                    else:
                        path = path_key                        
                    self.page_msg.red(
                        "Error: Path '%s' doesn't exist" % path
                    )
                else:
                    self.page_msg("change base path to '%s'." % path_key)
                    return path_key
        else:
            form = SelectBasePathForm()
            
        context["select_basepath"] = form



class WrongBasePath(Exception):
    pass