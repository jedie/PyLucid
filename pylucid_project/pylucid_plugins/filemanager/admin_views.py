# coding:utf-8

"""
    filemanager admin views
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import os
import posixpath
import pwd

if __name__ == "__main__":
    # For doctest only
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"
    from django.conf import global_settings
    global_settings.SITE_ID = 1

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404

from django_tools.filemanager.filemanager import BaseFilemanager

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid_admin.admin_menu import AdminMenu

from pylucid_project.pylucid_plugins.filemanager.preference_forms import FilemanagerPrefForm
from pylucid_project.pylucid_plugins.filemanager.forms import BasePathSelect, \
    UploadFileForm




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

class Filemanager(BaseFilemanager):
    def __init__(self, url_prefix, request, absolute_path, base_url, rest_url, allow_upload):
        self.url_prefix = url_prefix # For building links to the files

        super(Filemanager, self).__init__(request, absolute_path, base_url, rest_url, allow_upload)

        pref_form = FilemanagerPrefForm()
        self.preferences = pref_form.get_preferences()

    def get_filesystem_item_instance(self, *args, **kwargs):
        """
        Add url to this filesystem item, if url_prefix was set in base path config
        """
        instance = super(Filemanager, self).get_filesystem_item_instance(*args, **kwargs)

        if self.url_prefix:
            instance.url = posixpath.join(self.url_prefix, self.rel_url, instance.name)
            if instance.is_dir:
                instance.url += "/"

        return instance

#-----------------------------------------------------------------------------

def _reverse_filemanager_url(base_path_no):
    url = reverse('Filemanager-filemanager',
        kwargs={"no": base_path_no, "rest_url":""}
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
                new_path = BasePathSelect.PATH_DICT[base_path_no]["abs_base_path"]
                messages.success(request, "Change base path to: '%s', ok." % new_path)
                return _redirect2filemanager(base_path_no)
    else:
        path_form = BasePathSelect({"base_path": no})
        if not path_form.is_valid():
            raise Http404("Wrong page path no: %r!" % no)

    path_config = BasePathSelect.PATH_DICT[no]
    base_url = _reverse_filemanager_url(no)

    absolute_path = path_config["abs_base_path"]
    url_prefix = path_config["url_prefix"]
    allow_upload = path_config["allow_upload"]

    fm = Filemanager(url_prefix, request, absolute_path, base_url, rest_url, allow_upload)

    if allow_upload:
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
        "path_form": path_form,

        "uid": uid,
        "gid": gid,
        "username": username,
        "groupname": groupname,

    }
    if allow_upload:
        context["upload_form"] = upload_form

    return context


if __name__ == "__main__":
    import doctest
    print doctest.testmod(
#        verbose=True
        verbose=False
    )
