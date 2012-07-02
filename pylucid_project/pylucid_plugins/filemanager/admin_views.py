# coding:utf-8

"""
    filemanager admin views
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from operator import attrgetter
import datetime
import os
import posixpath
import stat

if __name__ == "__main__":
    # For doctest only
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"
    from django.conf import global_settings
    global_settings.SITE_ID = 1

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid_admin.admin_menu import AdminMenu
from pylucid_project.filemanager.filemanager import BaseFilemanager
from pylucid_project.pylucid_plugins.filemanager.forms import BasePathSelect, \
    UploadFileForm
from pylucid_project.pylucid_plugins.filemanager.preference_forms import FilemanagerPrefForm
import pwd



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

def symbolic_notation(mode):
    """
    Convert os.stat().st_mode values to a symbolic representation. e.g: 
       
    >>> symbolic_notation(16893) # -> 040775 -> 775
    u'rwxrwxr-x'
    
    >>> symbolic_notation(33204) # -> 0100664 -> 664
    u'rw-rw-r--'
    """
    mode = mode & 0777 # strip "meta info"
    chmod_symbol = u''.join(
        mode & 0400 >> i and x or u'-' for i, x in enumerate(u'rwxrwxrwx')
    )
    return chmod_symbol


class FilesystemObject(object):
    def __init__(self, fm_instance, name, abs_path, link_path=None):
        self.fm_instance = fm_instance # Filemanager instance
        self.name = name # The name of the directory item
        self.abs_path = abs_path # absolute path to this dir item
        self.link_path = link_path # Only for links: the real path of the dir item

        self.base_path = self.fm_instance.abs_path # path in which this item exists

        self.stat = os.stat(self.abs_path)
        self.size = self.stat[stat.ST_SIZE]
        self.mode = self.stat[stat.ST_MODE]
        self.mtime = datetime.datetime.fromtimestamp(self.stat[stat.ST_MTIME])
        
        self.mode_octal = oct(self.mode)
        self.mode_symbol = symbolic_notation(self.mode)
        
        self.uid = self.stat[stat.ST_UID]
        self.username = pwd.getpwuid(self.uid).pw_name
        self.gid = self.stat[stat.ST_GID]
        self.groupname = pwd.getpwuid(self.gid).pw_name

        url_prefix = self.fm_instance.url_prefix
        if url_prefix:
            self.url = posixpath.join(url_prefix, self.fm_instance.rel_url, self.name)

    def __repr__(self):
        return "%s '%s' in %s" % (self.item_type, self.name, self.base_path)


class FileItem(FilesystemObject):
    is_file = True
    item_type = "file"
        

class DirItem(FilesystemObject):
    is_dir = True
    item_type = "dir"
    def __init__(self, *args, **kwargs):
        super(DirItem, self).__init__(*args, **kwargs)
        if self.fm_instance.url_prefix:
            self.url += "/" # add slash on all directory links


class FileLinkItem(FileItem):
    def __init__(self, *args, **kwargs):
        super(FileLinkItem, self).__init__(*args, **kwargs)
        self.item_type = "file link to %s" % self.link_path

class DirLinkItem(DirItem):
    def __init__(self, *args, **kwargs):
        super(FileLinkItem, self).__init__(*args, **kwargs)
        self.item_type = "dir link to %s" % self.link_path


class Filemanager(BaseFilemanager):
    def __init__(self, url_prefix, *args, **kwargs):
        super(Filemanager, self).__init__(*args, **kwargs)

        self.url_prefix = url_prefix

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

        # sort the dir items by name but directories first
        # http://wiki.python.org/moin/HowTo/Sorting/#Operator_Module_Functions
        dir_items = sorted(dir_items, key=attrgetter('item_type', 'name'))

        return dir_items

    def handle_uploaded_file(self, f):
        path = os.path.join(self.abs_path, f.name)
        destination = file(path, 'wb+')
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()

        messages.success(self.request,
            "File '%s' (%i Bytes) uploaded to %s" % (f.name, f.size, self.abs_path)
        )

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

    if request.method == "POST" and "base_path" in request.POST:
        path_form = BasePathSelect(request.POST)
        if path_form.is_valid():
            base_path_no = int(path_form.cleaned_data["base_path"])
            if not base_path_no == no:
                new_path = BasePathSelect.PATH_DICT[base_path_no]
                messages.success(request, "Change base path to: '%s', ok." % new_path)
                return _redirect2filemanager(base_path_no)
    else:
        path_form = BasePathSelect({"base_path": no})
        if not path_form.is_valid():
            raise Http404("Wrong page path no: %r!" % no)

    absolute_path = BasePathSelect.PATH_DICT[no]
    base_url = _reverse_filemanager_url(no)
    
    url_prefix = BasePathSelect.URL_DICT[no]

    fm = Filemanager(url_prefix, request, absolute_path, base_url, rest_url)

    if request.method == "POST" and "file" in request.FILES:
        upload_form = UploadFileForm(request.POST, request.FILES)
        if upload_form.is_valid():
            fm.handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect(request.path)
    else:
        upload_form = UploadFileForm()

    dir_items = fm.dir_items
    breadcrumbs = fm.breadcrumbs
    
    uid = os.geteuid()
    gid = os.getegid()
    username = pwd.getpwuid(uid).pw_name
    groupname = pwd.getpwuid(gid).pw_name

    context = {
        "title": "Filemanager",
        "dir_items": dir_items,
        "breadcrumbs": breadcrumbs,
        "upload_form": upload_form,
        "path_form": path_form,
        
        "uid": uid,
        "gid": gid,
        "username": username,
        "groupname": groupname,
        
    }
    return context


if __name__ == "__main__":
    import doctest
    print doctest.testmod(
#        verbose=True
        verbose=False
    )
