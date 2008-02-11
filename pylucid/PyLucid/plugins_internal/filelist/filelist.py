#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid media file manager
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    TODO:
        - rename some variables to better names
        - optimize the _action() method
        - merge in the template the dir_list and file_list loop
        - Write a unitest for the plugin and verify the "bad-char-things" in
            path/post variables.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: $
    $Rev:  $
    $Author: $

    :copyleft: Ibon, Jens Diemer
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__= ""

import os, sys, stat
from time import localtime, strftime

from django import newforms as forms
from django.utils.translation import ugettext as _

from PyLucid import settings
from PyLucid.models import Page
from PyLucid.system.BasePlugin import PyLucidBasePlugin


ABS_PATH = os.path.abspath(settings.MEDIA_ROOT)


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




class filelist(PyLucidBasePlugin):

    def getFilesList(self, rel_dir):
        """
        Returns all file in dir current_dir
         'relative' to url root

        """
        listFile=[]

        if not rel_dir:
            # current dir it the media Root
            listDir=[]
        else:
            # Add the ".." dir item
            updir = os.path.split(rel_dir)[0]
            listDir = [{
                "name": "..",
                "dir_link": self.URLs.methodLink(
                    method_name="lucidTag", args=updir
                ),
                "deletable": False,
            }]

        # convert the relative path to absolute filesystem path
        abs_fs_path=os.path.join(ABS_PATH, rel_dir)

        if not abs_fs_path.startswith(ABS_PATH):
            raise WrongDirectory(abs_fs_path)
            #return listDir,listFile

        for item in os.listdir(abs_fs_path):
            if item.startswith("."):
                # skip hidden files or dirs
                continue

            item_rel_dir = os.path.join(rel_dir, item)
            item_abs_fs_path = os.path.join(abs_fs_path, item)
            statinfo = os.stat(item_abs_fs_path)

            item_dict={
                "name": item,
                "title": item_abs_fs_path,
                "time": strftime("%Y:%m:%M",localtime(statinfo[stat.ST_MTIME])),
                "size": statinfo[stat.ST_SIZE],
                "mode": statinfo[stat.ST_MODE],
                "uid": statinfo[stat.ST_UID],
                "gid": statinfo[stat.ST_GID],
                "deletable": True,
            }
            if stat.S_ISDIR(statinfo[stat.ST_MODE]):
                item_dict["dir_link"] = self.URLs.methodLink(
                    method_name="lucidTag", args=item_rel_dir
                )
                listDir.append(item_dict)
            else:
                listFile.append(item_dict)

        return listDir,listFile


    def make_dir_links(self, path):
        """
        path: /data/one/two

        return [('/data/one/two','two'), ('/data/one','one'),('/data','data')]
        """
        dir_links = [{
            # Display only the short relative path:
            "name": os.path.normpath(settings.MEDIA_ROOT),
            "title": ABS_PATH,
            "link": self.URLs.methodLink(method_name="lucidTag"),
        }]
        if path:
            # Not in the root
            dirlist = make_dirlist(path, [])
            for path, name in dirlist:
                dir_links.append({
                    "name": name,
                    "title": os.path.join(ABS_PATH, path),
                    "link": self.URLs.methodLink(
                        method_name="lucidTag", args=path
                    ),
                })

        return dir_links

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

        if action=='del':
            check_filename(filename)
            try:
                os.remove(file_abs)
            except Exception, e:
                self.page_msg.red("Can't delete '%s': %s" % (filename, e))
            else:
                self.page_msg.green("File '%s' deleted successfull." % filename)

        if action=='deldir':
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

        elif action=='mdir':
            check_path(filename)
            if file_abs.startswith("."):
                self.page_msg.red("Error?!?")
                return os.path.normpath(dir_string)

            try:
                os.mkdir(file_abs)
            except Exception, e:
                self.page_msg.red("Can't create '%s': %s" % (filename, e))
            else:
                self.page_msg.green("'%s' creaded successfull." % filename)

    def userinfo(self):
        self.page_msg("uid:", os.getuid())
        self.page_msg("gid:", os.getgid())
        import pwd, grp
        self.page_msg(pwd.getpwuid(os.getuid()))
        self.page_msg(grp.getgrgid(os.getgid()))


    def lucidTag(self, rest=''):
        """
        List dir and file. Some actions.
        rest: path to dir or file
        """
        # Change the global page title:
        self.context["PAGE"].title = _("File list")
        context = {}
        dir_list = []
        files_list = []

        dir_string=''

        if rest!='':
#            self.page_msg("rest:", rest)
            dir_string=os.path.normpath(rest)

        if self.request.method == 'POST':
#            self.page_msg(self.request.POST)
            dir_string=os.path.normpath(self.request.POST['dir_string'])

            if self.request.has_key('action'):

                filename = self.request['filename']
                check_filename(filename)
                filename=os.path.normpath(filename)

                self._action(dir_string, filename, self.request['action'])

            elif self.request.FILES.has_key('ufile'):
                """
                uploading a file
                """
                files=self.request.FILES['ufile']
                filename = files['filename']
                check_filename(filename)
                filename = os.path.normpath(filename)

                pathFile = os.path.abspath(
                    os.path.join(ABS_PATH, dir_string, filename)
                )
                try:
                    fileLike = file(pathFile,'wb') #if it exists, overwrite
                    fileLike.write(files['content'])
                    fileLike.close()
                except Exception, e:
                    self.page_msg.red("Can't write file: '%s'" % e)
                else:
                    self.page_msg.green(
                        "File '%s' written successfull." % filename
                    )

        abs_path = os.path.join(ABS_PATH, dir_string)

#        self.page_msg("read dir '%s'" % dir_string)
        dir_list,files_list = self.getFilesList(dir_string)

        context = {
            "url": self.URLs.methodLink("lucidTag"),
            "dir": dir_string,
            "dir_links": self.make_dir_links(dir_string),
            "writeable": os.access(abs_path, os.W_OK),
            "files_list": files_list,
            "dir_list": dir_list,
            "abs_path": ABS_PATH,
            "messages": self.page_msg,
            "commandURLprefix": self.URLs.get_command_base(),
        }

#        self._render_template("file_form", context, debug=True)
        self._render_template("file_form", context)#, debug=True)




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

