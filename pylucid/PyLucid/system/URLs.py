# -*- coding: utf-8 -*-
"""
    PyLucid URLs
    ~~~~~~~~~~~~

    The URLs class has some usefull methods for plugins to build links.
    Also the class has some joined media path information, for create urls and
    filesystem path to the media and internal page files.

    The view put a instance in context["URLs"]. The BasePlugin bind the class
    to self. So every plugin can easy access the methods with self.URLs.

    more info: http://pylucid.org/_goto/62/self-URLs/

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os, posixpath

from django.conf import settings
from django.utils.http import urlquote_plus


def add_trailing_slash(path):
    """
    >>> add_trailing_slash("/noSlash")
    '/noSlash/'
    >>> add_trailing_slash("/hasSlash/")
    '/hasSlash/'
    """
    if path=="" or path[-1]!="/":
        return path+"/"
    else:
        return path

def join_url(base, parts=None, args=None):
    """
    -join the url parts >base<, >parts< and >args< together
    -quote every part of the url
    -Always add a trailing slash!

    >>> join_url("1")
    u'1/'
    >>> join_url(1, [2,3])
    u'1/2/3/'
    >>> join_url("/1/", [2,3])
    u'/1/2/3/'
    >>> join_url("1", [2,3], ("/4/","/5/"))
    u'1/2/3/4/5/'
    """
    def get_quoted_list(item, safe="/"):
        """
        -convert the item into a list
        -quote every part of the list
        """
        if item == None:
            return []
        elif isinstance(item, tuple):
            item_list = list(item)
        elif isinstance(item, list):
            item_list = item
        else:
            item_list = [item]

        return [urlquote_plus(entry, safe) for entry in item_list]

    # Note: base can start with e.g.: "http://foobar", so we set 'safe'
    base = get_quoted_list(base, safe=':/')
    parts = get_quoted_list(parts)
    args = get_quoted_list(args)

    # join all list parts together
    part_list = base + parts + args

    # sript every "/" out, but not for the first and the last entry:
    index_list = range(len(part_list))[1:-1]
    for index in index_list:
        part_list[index] = part_list[index].strip("/")

    # remove a trailing slash from the first item:
    part_list[0] = part_list[0].rstrip("/")

    # remove a leading slash from the last item:
    part_list[-1] = part_list[-1].lstrip("/")

    url = "/".join(part_list)
    url = add_trailing_slash(url)

    return url


class URLs(dict):
    def __init__(self, context):
        self.context     = context
        self.request     = context["request"]
        self.page_msg    = self.request.page_msg

        # Would be set by plugin_manager
        self.current_plugin = None

        self.setup_mediapath()
        self.setup_URLs()

    def setup_mediapath(self):
        """
        Set some shared used media path information to build url and filesystem
        path to the media and internal page files.
        About the internal_page stuff see DocString in system/internal_page.py
        """
        self["PyLucid_media_url"] = posixpath.join(
            settings.MEDIA_URL,
            settings.PYLUCID_MEDIA_DIR,
        )
        self["pylucid_media_root"] = os.path.join(
            settings.MEDIA_ROOT,
            settings.PYLUCID_MEDIA_DIR,
        )
        #----------------------------------------------------------------------
        self["internal_page_url"] = posixpath.join(
            self["PyLucid_media_url"],
            settings.INTERNAL_PAGE_DIR,
        )
        self["internal_page_root"] = os.path.join(
            self["pylucid_media_root"],
            settings.INTERNAL_PAGE_DIR,
        )
        #----------------------------------------------------------------------
        self["custom_internal_page_url"] = posixpath.join(
            self["PyLucid_media_url"],
            settings.CUSTOM_INTERNAL_PAGE_DIR,
        )
        self["custom_internal_page_root"] = os.path.join(
            self["pylucid_media_root"],
            settings.CUSTOM_INTERNAL_PAGE_DIR,
        )

    def setup_URLs(self):
        """
        Set some base urls, which are same for every Request and inside the
        response would be built.
        """
        self["cwd"] = os.getcwdu()
        self["host"] = self.request.get_host()
        self["hostname"] = "%s://%s" % (
            self.request.META.get('wsgi.url_scheme', "http"),
            self["host"],
        )

        self["path_info"] = self.request.META.get("PATH_INFO", "")

#        self["scriptRoot"] = self.request.META.get("SCRIPT_NAME", "/")
        self["scriptRoot"] = "/"

        self["docRoot"] = add_trailing_slash(posixpath.split(self["scriptRoot"])[0])

        self["absoluteIndex"] = add_trailing_slash(
            "".join((self["hostname"], self["scriptRoot"]))
        )
        self["adminBase"] = posixpath.join(
            self["scriptRoot"], settings.ADMIN_URL_PREFIX
        )

    #__________________________________________________________________________

    def get_command_base(self):
        """
        Generate the command base for self.commandLink() and self.methodLink().
        Note: This is extra not build in self.setup_URLs(), because a Plugin
        can change the current page!
        e.g.: After a new page created, PyLucid goto this new page and every
        command/method link should use the new page id.
        """
        return posixpath.join(
            self["scriptRoot"], settings.COMMAND_URL_PREFIX,
            str(self.context["PAGE"].id)
        )

    def commandLink(self, plugin_name, method_name, args=None):
        """
        generate a command link
        """
        command_base = self.get_command_base()
        parts = [plugin_name, method_name]
        return join_url(command_base, parts, args)

    def methodLink(self, method_name, args=None):
        """
        generate a link to a other method in the current used plugin.
        """
        command_base = self.get_command_base()
        parts = [self.current_plugin, method_name]
        return join_url(command_base, parts, args)

    def adminLink(self, url):
        """
        generate a link into the django admin panel.
        """
        return join_url(self["adminBase"], url)

    #__________________________________________________________________________

    def make_absolute_url(self, link):
        """
        make the given link to a absolute url.
        """
        return join_url(self["hostname"], link)

    #__________________________________________________________________________

    def debug(self):
        """
        write debug information into the page_msg
        """
        self.page_msg("URLs debug:")
        for k,v in self.items():
            self.page_msg(" - %15s: '%s'" % (k,v))



def _doc_test(verbose):
    global DEBUG
    DEBUG = True

    import doctest
    doctest.testmod(verbose=verbose)


if __name__ == "__main__":
    print "Start a DocTest..."
#    _doc_test(verbose=False)
    _doc_test(verbose=True)
    print "DocTest end."
    print
    print "Note:"
    print "You should run ./dev_scripts/unittests/unittest_URLs.py !"