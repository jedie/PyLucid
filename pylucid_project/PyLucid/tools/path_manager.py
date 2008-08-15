# -*- coding: utf-8 -*-

"""
    PyLucid path manager
    ~~~~~~~~~~~~~~~~~~~~

    Tools around handling path in PyLucid.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

import os, posixpath, dircache

if __name__ == "__main__":
    from PyLucid import settings
else:
    from django.conf import settings

#______________________________________________________________________________
# Build a list and a dict from the basepaths
# The dict key is a string, not a integer. (GET/POST Data always returned
# numbers as strings)

BASE_PATHS = [
    (str(no), unicode(path)) for no, path in enumerate(
                                                settings.FILEMANAGER_BASEPATHS)
]
BASE_PATHS_DICT = dict(BASE_PATHS)

#______________________________________________________________________________

def _dir_walk(path):
    result = []
    for name in dircache.listdir(path):
        if name.startswith("."):
            continue

        abs_path = os.path.join(path, name)
        if not os.path.isdir(abs_path):
            continue

        result.append(abs_path)
        result.extend(_dir_walk(abs_path))

    return result

#______________________________________________________________________________


class MediaPath(object):
    """
    A class for handling media url/path.

    >>> mp = MediaPath("/fs/path/to/media/", "/media/url/")

    >>> mp.clean_media_path("/fs/path/to/media/filename.txt")
    'filename.txt'
    >>> mp.clean_media_path("/fs/path/to/media/dir/filename.txt")
    'dir/filename.txt'

    >>> mp.get_media_url("/fs/path/to/media/filename.txt")
    'media/url/filename.txt'
    >>> mp.get_media_url("/fs/path/to/media/dir/filename.txt")
    'media/url/dir/filename.txt'

    >>> mp.join_media_path("/dir1/filename.txt")
    '/fs/path/to/media/dir1/filename.txt'
    >>> mp.join_media_path("filename.txt")
    '/fs/path/to/media/filename.txt'
    >>> mp.join_media_path("/filename.txt")
    '/fs/path/to/media/filename.txt'
    >>> mp.join_media_path("./filename.txt")
    '/fs/path/to/media/filename.txt'

    >>> mp.join_media_url("/dir1/filename.txt")
    '/media/url/dir1/filename.txt'
    >>> mp.join_media_url("filename.txt")
    '/media/url/filename.txt'
    >>> mp.join_media_url("/filename.txt")
    '/media/url/filename.txt'
    >>> mp.join_media_url("./filename.txt")
    '/media/url/filename.txt'
    """

    _MEDIA_DIR_CACHE = None

    def __init__(self, media_root, media_url):
        self.media_root = os.path.normpath(media_root)
        self.media_root_len = len(self.media_root)

        self.media_url = posixpath.normpath(media_url)
        self.media_url_len = len(self.media_url)


    def get_media_dirs(self):
        """
        returns a cached list of all media path directories.
        """
        if self._MEDIA_DIR_CACHE == None:
            self._MEDIA_DIR_CACHE = _dir_walk(self.media_root)
            self._MEDIA_DIR_CACHE.sort()
            self._MEDIA_DIR_CACHE = tuple(self._MEDIA_DIR_CACHE)

        return self._MEDIA_DIR_CACHE


    def get_media_url(self, fs_path):
        """
        Returns the URL to the given filesystem path.
        """
        fs_path2 = self.clean_media_path(fs_path)

        url = posixpath.join(self.media_url, fs_path2)
        url = url.lstrip("./")

        return url

    def clean_media_path(self, path):
        """
        strips settings.MEDIA_ROOT out from the path.
        """
        path2 = os.path.normpath(path)

        if path2.startswith(self.media_root):
            path2 = path2[self.media_root_len:]
            path2 = path2.lstrip("./")

        return path2

    def join_media_path(self, rel_fs_path):
        """
        merge settings.MEDIA_ROOT with the given file path.
        """
        rel_fs_path2 = os.path.normpath(rel_fs_path)
        rel_fs_path2 = rel_fs_path2.lstrip("./")
        return os.path.join(self.media_root, rel_fs_path2)

    def abs_media_path(self, rel_fs_path):
        """
        Returns the absolute filepath to the media file.
        """
        return os.path.abspath(self.join_media_path(rel_fs_path))

    def join_media_url(self, rel_fs_path):
        """
        create a absolute URL to the media file.
        """
        rel_fs_path2 = posixpath.normpath(rel_fs_path)
        rel_fs_path2 = rel_fs_path2.lstrip("./")
        return posixpath.join(self.media_url, rel_fs_path2)


if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
else:
    media_path_helper = MediaPath(settings.MEDIA_ROOT, settings.MEDIA_URL)