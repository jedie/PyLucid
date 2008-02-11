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




class filemanager(PyLucidBasePlugin):

    def getFilesList(self, rel_dir):
        """
        Returns all items in the given directory.
        -rel_dir is relative to ABS_PATH
        -the listing is sorted and the first items are the directories.
        """
        files = []

        if not rel_dir:
            # current dir it the media Root
            dirs=[]
        else:
            # Add the ".." dir item
            updir = os.path.split(rel_dir)[0]
            dirs = [{
                "name": "..",
                "link": self.URLs.methodLink(
                    method_name="filelist", args=updir
                ),
                "is_dir": True,
                "deletable": False,
            }]

        # convert the relative path to absolute filesystem path
        abs_fs_path=os.path.join(ABS_PATH, rel_dir)

        if not abs_fs_path.startswith(ABS_PATH):
            raise WrongDirectory(abs_fs_path)

        link_prefix = self.URLs.methodLink(method_name="filelist")

        for item in sorted(os.listdir(abs_fs_path)):
            if item.startswith("."):
                # skip hidden files or directories
                continue

            item_abs_fs_path = os.path.join(abs_fs_path, item)
            statinfo = os.stat(item_abs_fs_path)

            link = os.path.join(link_prefix, rel_dir, item)

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
                "title": item_abs_fs_path,
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


    def make_dir_links(self, path):
        """
        path: /data/one/two

        return [('/data/one/two','two'), ('/data/one','one'),('/data','data')]
        """
        dir_links = [{
            # Display only the short relative path:
            "name": os.path.normpath(settings.MEDIA_ROOT),
            "title": ABS_PATH,
            "link": self.URLs.methodLink(method_name="filelist"),
        }]
        if path:
            # Not in the root
            dirlist = make_dirlist(path, [])
            for path, name in dirlist:
                dir_links.append({
                    "name": name,
                    "title": os.path.join(ABS_PATH, path),
                    "link": self.URLs.methodLink(
                        method_name="filelist", args=path
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

    def filelist(self, rest=''):
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
        dir_list = self.getFilesList(dir_string)

        context = {
            "url": self.URLs.methodLink("filelist"),
            "dir": dir_string,
            "dir_links": self.make_dir_links(dir_string),
            "writeable": os.access(abs_path, os.W_OK),
            "dir_list": dir_list,
            "abs_path": ABS_PATH,
            "messages": self.page_msg,
            "userinfo_link": self.URLs.methodLink(
                method_name="userinfo", args=dir_string
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

