# coding:utf-8

"""
    filemanager admin views
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import stat
from operator import attrgetter

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid_admin.admin_menu import AdminMenu
from pylucid_project.filemanager.filemanager import BaseFilemanager
from pylucid_project.pylucid_plugins.filemanager.forms import BasePathSelect
from pylucid_project.pylucid_plugins.filemanager.preference_forms import FilemanagerPrefForm



def install(request):
    """ insert PyLucid admin views into PageTree """
    output = []

    admin_menu = AdminMenu(request, output)
    menu_section_entry = admin_menu.get_or_create_section("tools")

    admin_menu.add_menu_entry(
        parent=menu_section_entry,
        name="filemanager", title="Filemanager for static/media files",
        url_name="Filemanager-index"
    )

    return "\n".join(output)

#-----------------------------------------------------------------------------


class FilesystemObject(object):
    def __init__(self, fm_instance, name, abs_path, link_path=None):
        self.fm_instance = fm_instance # Filemanager instance
        self.name = name # The name of the directory item
        self.abs_path = abs_path # absolute path to this dir item
        self.link_path = link_path # Only for links: the real path of the dir item

        self.base_path = self.fm_instance.abs_path # path in which this item exists

        self.stat = os.stat(self.abs_path)
        self.size = self.stat[stat.ST_SIZE]

        self.item_type = None

    def __repr__(self):
        return "%s '%s' in %s" % (self.item_type, self.name, self.base_path)


class FileItem(FilesystemObject):
    is_file = True
    item_type = "file"

class DirItem(FilesystemObject):
    is_dir = True
    item_type = "dir"


class FileLinkItem(FileItem):
    def __init__(self, *args, **kwargs):
        super(FileLinkItem, self).__init__(*args, **kwargs)
        self.item_type = "file link to %s" % self.link_path

class DirLinkItem(DirItem):
    def __init__(self, *args, **kwargs):
        super(FileLinkItem, self).__init__(*args, **kwargs)
        self.item_type = "dir link to %s" % self.link_path


class Filemanager(BaseFilemanager):
    def __init__(self, *args, **kwargs):
        super(Filemanager, self).__init__(*args, **kwargs)

        pref_form = FilemanagerPrefForm()
        self.preferences = pref_form.get_preferences()

        self.dir_items = self.read_dir(self.abs_path)

    def read_dir(self, path):
        dir_items = []
        for item in os.listdir(path):
            item_abs_path = os.path.join(self.abs_path, item)
            link_path = None
            if os.path.islink(item_abs_path):
                link_path = os.readlink(item_abs_path)
                if os.path.isdir(link_path):
                    item_class = DirLinkItem
                elif os.path.isfile(link_path):
                    item_class = FileLinkItem
                else:
                    raise NotImplemented
            elif os.path.isdir(item_abs_path):
                item_class = DirItem
            elif os.path.isfile(item_abs_path):
                item_class = FileItem
            else:
                messages.info(self.request, "unhandled direcory item: %r" % self.abs_path)
                continue

            instance = item_class(self, item, item_abs_path, link_path)
            dir_items.append(instance)

        # http://wiki.python.org/moin/HowTo/Sorting/#Operator_Module_Functions
        dir_items = sorted(dir_items, key=attrgetter('item_type', 'name'))

        return dir_items

#-----------------------------------------------------------------------------

def _reverse_filemanager_url(base_path_no):
    url = reverse('Filemanager-filemanager',
        kwargs={"no": base_path_no, "rest_url":"/"}
    )
    return url

def _redirect2filemanager(base_path_no):
    url = _reverse_filemanager_url(base_path_no)
    return HttpResponseRedirect(url)


@check_permissions(superuser_only=True)
def index(request):
    form = BasePathSelect()
    initial_base_path = form.fields["base_path"].initial
    base_path_no = initial_base_path[0]
    return _redirect2filemanager(base_path_no)


@check_permissions(superuser_only=True)
@render_to("filemanager/default.html")
def filemanager(request, no, rest_url=""):
    no = int(no)
    if request.method == "POST":
        form = BasePathSelect(request.POST)
        if form.is_valid():
            base_path_no = int(form.cleaned_data["base_path"])
            if not base_path_no == no:
                new_path = BasePathSelect.PATH_DICT[base_path_no]
                messages.success(request, "Change base path to: '%s', ok." % new_path)
                return _redirect2filemanager(base_path_no)
    else:
        form = BasePathSelect({"base_path": no})
        if not form.is_valid():
            raise Http404("Wrong page path no: %r!" % no)

    absolute_path = BasePathSelect.PATH_DICT[no]
    base_url = _reverse_filemanager_url(no)

    fm = Filemanager(request, absolute_path, base_url, rest_url)
    dir_items = fm.dir_items
    breadcrumbs = fm.breadcrumbs

    context = {
        "title": "Filemanager",
        "dir_items": dir_items,
        "breadcrumbs": breadcrumbs,
        "form": form,
    }
    print context
    return context
