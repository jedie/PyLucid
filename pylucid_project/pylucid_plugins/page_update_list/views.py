# -*- coding: utf-8 -*-

"""
    PyLucid page update list plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Generate a list of the latest page updates.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.p

"""

__version__ = "$Rev$"

from django.conf import settings

from pylucid.decorators import render_to

from pylucid_project.system.pylucid_plugins import PYLUCID_PLUGINS


class UpdateListItem(object):
    """ One item in the last update list """
    def __init__(self, lastupdatetime, lastupdateby, content_type, language, url, title):
        self.lastupdatetime = lastupdatetime
        self.lastupdateby = lastupdateby
        self.content_type = content_type
        self.language = language
        self.url = url
        self.title = title

class UpdateList(object):
    """ All update list """
    def __init__(self, request, max_count):
        self.request = request
        self.max_count = max_count
        self.updates = []

    def add(self, lastupdatetime, lastupdateby, content_type, language, url, title):
        """ add a new update list item """
        update_item = UpdateListItem(lastupdatetime, lastupdateby, content_type, language, url, title)
        self.updates.append(update_item)

    def collect_all(self):
        method_kwargs = {"update_list":self, "max_count":self.max_count}
        filename = settings.PYLUCID.UPDATE_LIST_FILENAME
        view_name = settings.PYLUCID.UPDATE_LIST_VIEWNAME
        for plugin_name, plugin_instance in PYLUCID_PLUGINS.iteritems():
            try:
                plugin_instance.call_plugin_view(self.request, filename, view_name, method_kwargs)
            except Exception, err:
                if not str(err).endswith("No module named %s" % filename):
                    raise

    def __iter__(self):
        for no, update in enumerate(sorted(self.updates, key=lambda x: x.lastupdatetime, reverse=True)):
            if no >= self.max_count:
                raise StopIteration
            yield update


@render_to("page_update_list/PageUpdateTable.html")
def lucidTag(request, count=10):
    try:
        count = int(count)
    except Exception, e:
        if request.user.is_stuff():
            request.page_msg.error("page_update_list error: count must be a integer (%s)" % e)
        count = 10


    print "start"
    update_list = UpdateList(request, count)
    update_list.collect_all()


    # TODO:
#    if not request.user.is_staff:
#        pages = pages.filter(showlinks = True)
#        pages = pages.exclude(permitViewPublic = False)
#
    return {"update_list": update_list}

