# coding: utf-8


"""
    PyLucid App. settings
    ~~~~~~~~~~~~~~~~~~~~~
    
    settings witch only used in the PyLucid app.
    
    :copyleft: 2009-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


# Every Plugin output gets a html DIV or SPAN tag around.
# Here you can defined witch CSS class name the tag should used:
CSS_PLUGIN_CLASS_NAME = "PyLucidPlugins"

HEADFILE_INLINE_TEMPLATES = "pylucid/headfile_%s_inline.html"
HEADFILE_LINK_TEMPLATES = "pylucid/headfile_%s_link.html"
HEAD_FILES_URL_PREFIX = "headfile"

PERMALINK_URL_PREFIX = "permalink"
OLD_PERMALINK_PREFIX = "_goto"

# i18n stuff:
I18N_DEBUG = False # Display many info around detecting current language

HTTP_GET_VIEW_NAME = "http_get_view"

# All PyLucid media files stored in a sub directory under the django media
# path. Used for building filesystem path and URLs.
# filesystem path: STATIC_ROOT + PYLUCID_MEDIA_DIR
# URLs: STATIC_URL + PYLUCID_MEDIA_DIR
PYLUCID_MEDIA_DIR = "PyLucid" # Without slashes at begin/end!

AUTH_LOGOUT_GET_VIEW = "auth=logout"
AUTH_GET_VIEW = "auth=login"
AUTH_NEXT_URL = "%%(path)s?%s&next_url=%%(next_url)s" % AUTH_GET_VIEW
# e.g.: settings.PYLUCID.AUTH_NEXT_URL % {"path": request.path, "next_url": url}


#UPDATE_LIST_FILENAME = "update_list"
#UPDATE_LIST_VIEWNAME = "get_update_list"
SEARCH_FILENAME = "search"
SEARCH_CLASSNAME = "Search"

# plugin update hook
UPDATE08_PLUGIN_FILENAME = "update"
UPDATE08_PLUGIN_VIEWNAME = "update08"

# Number of seconds after the IP ban cleanup method would be called.
# This removed the outdated IPs from the ban list.
CLEANUP_IP_BAN = 60
# How long should a IP address banned in minutes:
BAN_RELEASE_TIME = 15

# internal placeholder: The PyLucid TOC Plugin insert it and the HeadlineAnchorMiddleware
# replaced it with the Table of contents html code.
TOC_PLACEHOLDER = u"<!-- lucidTag TOC -->"
