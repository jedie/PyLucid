#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid media file manager
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    TODO:
        - add edit text files functionality
        - optimize the _action() method
        - Write a unitest for the plugin and verify the "bad-char-things" in
            path/post variables.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: Ibon, Jens Diemer
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__= "$Rev: $"

import os, cgi, sys, stat
from time import localtime, strftime

from django.http import Http404
from django import newforms as forms
from django.newforms.util import ValidationError
from django.utils.translation import ugettext as _

from PyLucid import settings
from PyLucid.models import Page
from PyLucid.system.BasePlugin import PyLucidBasePlugin

BASE_PATHS = [
    (str(no),path) for no,path in enumerate(settings.FILEMANAGER_BASEPATHS)
]
BASE_PATHS_DICT = dict(BASE_PATHS)

def make_dirlist(path, result=[]):
    """
    >>> make_dirlist("/data/one/two")
    [('data/one/two', 'two'), ('data/one', 'one'), ('data', 'data')]
    """
    path = path.strip("/")

    head, tail = os.path.split(path)
    result.append((path, tail))

    if head:
        # go recusive deeper
        return make_dirlist(head, result)
    else:
        result.reverse()
        return result


BAD_FILENAME_CHARS = ("/", "..", "\\")
def check_filename(filename):
    for char in BAD_FILENAME_CHARS:
        if char in filename:
            raise BadFilename("Character '%s' not allowed!" % char)


BAD_PATH_CHARS = (".", "..", "//", "\\\\")
def check_path(path):
    for char in BAD_PATH_CHARS:
        if char in path:
            raise BadPath("Character '%s' not allowed!" % char)



class EditFileForm(forms.Form):
    """ Edit a text file form """
    content = forms.CharField()

class SelectBasePathForm(forms.Form):
    """ change the base path form """
    base_path = forms.ChoiceField(choices=BASE_PATHS)


class DirnameField(forms.CharField):
    """
    Verify a dirname
    """
    BAD_PATH_CHARS = ("..", "//", "\\\\")

    def __init__(self, max_length=255, min_length=1, required=True,
                                                            *args, **kwargs):
        super(DirnameField, self).__init__(
            max_length, min_length, required, *args, **kwargs
        )

    def clean(self, value):
        """
        """
        super(DirnameField, self).clean(value)
        if value.startswith("."):
            raise ValidationError(_(u"Hidden dirnames not allowed"))

        for char in self.BAD_PATH_CHARS:
            if char in value:
                raise ValidationError(_(u"Character '%s' not allowed!" % char))
        return value


class ActionField(forms.CharField):
    """
    A spezial HiddenInput field for the action string.
    The action string is set in the forms.Form class and must be the same in
    the POST data, otherwise the form is not valid.
    """
    def __init__(self, action):
        self.action = action
        max_length = min_length = len(action)
        super(ActionField, self).__init__(
            max_length=max_length, min_length=min_length,
            required=True, initial=action,
            widget=forms.HiddenInput,
        )

    def clean(self, value):
        super(ActionField, self).clean(value)
        if value != self.action:
            raise ValidationError(_(u"Wrong action!"))
        return value


class CreateDirForm(forms.Form):
    """
    Form for creating a new directory
    ToDo: add a choice field for create a file or a directory action
    """
    action = ActionField("mkdir")
    dirname = DirnameField(
        help_text="Create a new directory into the current directory."
    )


class UploadFileForm(forms.Form):
    """ Form to upload a new file """
    action = ActionField("fileupload")
    ufile = forms.FileField(
        label="filename",
        help_text="Upload a new file into the current directory."
    )



class filemanager(PyLucidBasePlugin):

    def getFilesList(self, base_no, abs_path, rel_path):
        """
        Returns all items in the given directory.
        -rel_dir is relative to ABS_PATH
        -the listing is sorted and the first items are the directories.
        """
        files = []

        if rel_path == ".":
            # current dir it the media Root
            dirs=[]
        else:
            # Add the ".." dir item
            updir = os.path.split(rel_path)[0]
            dirs = [{
                "name": "..",
                "link": self.URLs.methodLink(
                    method_name="filelist", args=(base_no, updir)
                ),
                "is_dir": True,
                "deletable": False,
            }]

        link_prefix = self.URLs.methodLink(method_name="filelist", args=base_no)

        for item in sorted(os.listdir(abs_path)):
            if item.startswith("."):
                # skip hidden files or directories
                continue

            abs_item_path = os.path.join(abs_path, item)
            statinfo = os.stat(abs_item_path)

            link = os.path.join(link_prefix, rel_path, item)

            if stat.S_ISDIR(statinfo[stat.ST_MODE]):
                # Is a directory
                is_dir = True
                link += "/"
            else:
                is_dir = False

            item_dict={
                "name": item,
                "link": link,
                "is_dir": is_dir,
                "title": abs_item_path,
                "time": strftime("%Y:%m:%M",localtime(statinfo[stat.ST_MTIME])),
                "size": statinfo[stat.ST_SIZE],
                "mode": statinfo[stat.ST_MODE],
                "uid": statinfo[stat.ST_UID],
                "gid": statinfo[stat.ST_GID],
                "deletable": True,
            }
            if is_dir:
                dirs.append(item_dict)
            else:
                files.append(item_dict)

        # return the merged list of direcories and files together
        dir_list = dirs + files
        return dir_list


    def make_dir_links(self, base_no, base_path, abs_path, rel_path):
        """
        Build the context for the path link line.
        Use the function make_dirlist().
        """
#        self.page_msg("base_no:", base_no, "base_path:", base_path)
#        self.page_msg("abs_path:", abs_path, "rel_path:", rel_path)

        # start with the first base_path entry:
        dir_links = [{
            "name": base_path, # use only the short relative path
            "title": abs_path,
            "link": self.URLs.methodLink(method_name="filelist", args=base_no),
        }]
        if rel_path != ".":
            # Not in the root
            dirlist = make_dirlist(rel_path, [])
            for path, name in dirlist:
                # append every dir "steps"
                dir_links.append({
                    "name": name,
                    "title": os.path.join(base_path, path),
                    "link": self.URLs.methodLink(
                        method_name="filelist", args=(base_no, path)
                    ),
                })

        return dir_links

    def edit(self, sourcepath):
        """
        Edit a text file.
        not ready yet!
        """
#        self.page_msg("sourcepath:", sourcepath)
        sourcepath = os.path.normpath(sourcepath)
        path, filename = os.path.split(sourcepath)
        check_path(path)
        check_filename(filename)
        self.page_msg("path:", path, "filename:", filename)

        abs_fs_path = os.path.join(ABS_PATH, path, filename)

        if not os.path.isfile(abs_fs_path):
            self.page_msg.red("Error: Given path is not a file!")
            return

        try:
            f = file(abs_fs_path, "r")
            content = f.read()
            f.close()
        except Exception, e:
            self.page_msg.red("Error, reading file:", e)
            return

        if self.request.method == 'POST':
            form = EditFileForm(self.request.POST)
            if form.is_valid():
                self.page_msg("Net implemented yet!!!")
        else:
            form = EditFileForm({"content": cgi.escape(content)})

        context = {
            "filename": filename,
            "form": form,

        }
        self._render_template("edit_file", context)#, debug=True)


    def action_mkdir(self, abs_path, dirname):
        """
        create a new directory
        """
        abs_new_path = os.path.join(abs_path, dirname)
        try:
            os.mkdir(abs_new_path)
        except Exception, e:
            self.page_msg.red("Can't create '%s': %s" % (dirname, e))
        else:
            self.page_msg.green("'%s' creaded successfull." % dirname)

    def action_fileupload(self, abs_path, filename, content):
        """
        save a uploaded file
        """
        check_filename(filename)
        abs_fs_path = os.path.join(abs_path, filename)

        try:
            f = file(abs_fs_path,'wb') #if it exists, overwrite
            f.write(content)
            f.close()
        except Exception, e:
            self.page_msg.red("Can't write file: '%s'" % e)
        else:
            self.page_msg.green(
                "File '%s' written successfull." % filename
            )

    def _action(self, dir_string, filename, action, dest=''):
        """
        Diferent actions over file or dir
        """
#        self.page_msg(
#            "dir_string:", dir_string, "filename:", filename,
#            "Action:", action, "dest:", dest
#        )

        file_rel=os.path.normpath(os.path.join(dir_string, filename))
        file_abs=os.path.abspath(os.path.join(ABS_PATH, file_rel))

        if not file_abs.startswith(ABS_PATH) or "/":
            WrongDirectory(file_abs)

        if action=="remove_file":
            check_filename(filename)
            try:
                os.remove(file_abs)
            except Exception, e:
                self.page_msg.red("Can't delete '%s': %s" % (filename, e))
            else:
                self.page_msg.green("File '%s' deleted successfull." % filename)

        if action=="rmdir":
            check_path(filename)
            try:
                os.rmdir(file_abs)
            except Exception, e:
                self.page_msg.red("Can't delete '%s': %s" % (filename, e))
            else:
                self.page_msg.green("'%s' deleted successfull." % filename)

#        if action=='rename':
#            check_filename(filename)
#            try:
#                os.rename(file_abs, dest)
#            except Exception, e:
#                self.page_msg.red(
#                    "Can't rename '%s' to '%s': %s" % (filename, dest, e)
#                )
#            else:
#                self.page_msg.green(
#                    "file '%s' renamed to '%s'." % (filename, dest)
#                )


    def userinfo(self, old_path=""):
        """
        Display some user information related to the filemanager functionality.
        """
        import pwd, grp

        uid = os.getuid()
        gid = os.getgid()

        pwd_info = pwd.getpwuid(os.getuid())
        grp_info = grp.getgrgid(os.getgid())

        context = {
            "filelist_link": self.URLs.methodLink(
                method_name="filelist", args=old_path
            ),
            "uid": uid,
            "gid": gid,
            "pwd_info": pwd_info,
            "grp_info": grp_info,
        }
#        self.page_msg(context)
        self._render_template("userinfo", context)#, debug=True)

    def select_basepath(self):
        """
        change the basepath, after send the form, we display the filelist
        """
#        self.page_msg(self.request.POST)

        if self.request.method == 'POST':
            form = SelectBasePathForm(self.request.POST)
            if form.is_valid():
                path_no = form.cleaned_data["base_path"]
                new_path = BASE_PATHS_DICT[path_no]
                if not os.path.isdir(new_path):
                    self.page_msg.red("Error: Path '%s' doesn't exist" % new_path)
                else:
                    self.page_msg("changed to '%s'." % new_path)
                    # Display the filelist:
                    return self.filelist(path_no + "/")
        else:
            form = SelectBasePathForm()

        self._render_template("select_basepath", {"form": form})#, debug=True)


    def filelist(self, path_info=None):
        """
        List dir and file. Some actions.
        rest: path to dir or file
        """
        if not path_info:
            self.select_basepath()
            return

#        try:
        base_no, rel_path = path_info.split("/", 1)
        rel_path = os.path.normpath(rel_path)
        base_path = os.path.normpath(BASE_PATHS_DICT[base_no])
#        except Exception, e:
#            self.page_msg.red("Path error:", e)
#            return

        abs_base_path = os.path.abspath(base_path)

        abs_path = os.path.normpath(os.path.join(abs_base_path, rel_path))
        if not os.path.isdir(abs_path):
            raise Http404(_("Error: Path '%s' doesn't exist.") % abs_path)

#        self.page_msg("base_no:", base_no, "base_path:", base_path)
#        self.page_msg("abs_base_path:", abs_base_path, "rel_path:", rel_path)

        # Change the global page title:
        self.context["PAGE"].title = _("File list")

        # We init all forms before we check the POST, because we only need
        # error information for the current action. Only the form for the
        # current action should be inited with self.request.POST!
        ufile_form = UploadFileForm()
        mkdir_form = CreateDirForm()

        if self.request.method == 'POST':
            self.page_msg(self.request.POST)

            action = self.request.POST["action"]
            if action == "mkdir":
                # Create a new directory
                mkdir_form = CreateDirForm(self.request.POST)
                if mkdir_form.is_valid():
                    dirname = mkdir_form.cleaned_data["dirname"]
                    self.action_mkdir(abs_path, dirname)

            elif action == "fileupload":
                # save a uploaded file
                ufile_form = UploadFileForm(
                    self.request.POST, self.request.FILES
                )
                if ufile_form.is_valid():
                    ufile = ufile_form.cleaned_data["ufile"]
                    filename = ufile.filename
                    content = ufile.content
                    self.action_fileupload(abs_path, filename, content)

        # build the directory+file list:
        dir_list = self.getFilesList(base_no, abs_path, rel_path)

        # Build the path link line:
        dir_links = self.make_dir_links(base_no, base_path, abs_path, rel_path)

        context = {
            "post_url": self.URLs.methodLink(
                method_name="filelist", args=(base_no, rel_path)
            ),

            "mkdir_form": mkdir_form,
            "ufile_form": ufile_form,

            "dir": rel_path,
            "dir_links": dir_links,
            "writeable": os.access(abs_path, os.W_OK),
            "dir_list": dir_list,
            "abs_path": abs_path,
            "messages": self.page_msg,
            "userinfo_link": self.URLs.methodLink(
                method_name="userinfo", args=rel_path
            ),
            "edit_link": self.URLs.methodLink(
                method_name="edit", args=rel_path
            ),
            "change_basepath_link": self.URLs.methodLink(
                method_name="select_basepath"
            ),
        }
#        self.page_msg(context)
#        self._render_template("filelist", context, debug=True)
        self._render_template("filelist", context)#, debug=True)




class WrongDirectory(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class BadFilename(Exception):
    """ A not allowed character contain a filename """
    pass

class BadPath(Exception):
    """ A not allowed character contain a path """
    pass

