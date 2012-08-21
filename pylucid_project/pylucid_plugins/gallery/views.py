# coding: utf-8


"""
    PyLucid gallery
    ~~~~~~~~~~~~~~~

    :copyleft: 2010-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from fnmatch import fnmatch
from glob import glob
import os
import posixpath

if __name__ == "__main__":
    # For doctest only
    from pylucid_project.tests import init_test_env
    init_test_env()

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponseBadRequest
from django.template.context import RequestContext
from django.utils.translation import ugettext as _

# TODO: Should be moved to django-tools!
from django_tools.filemanager.filemanager import FilemanagerError
from django_tools.filemanager.utils import add_slash
from django_tools.filemanager.filesystem_browser import BaseFilesystemBrowser

from pylucid_project.apps.pylucid.models import LogEntry
from pylucid_project.apps.pylucid.shortcuts import render_pylucid_response

from gallery.models import GalleryModel
from gallery.preference_forms import GalleryPrefForm


#------------------------------------------------------------------------------


def _fnmatch_list(item, filter_list):
    """
    case insensitive fnmatch with a list.
    
    >>> _fnmatch_list("foo.jpg", ["*.bar", "*.jpg"])
    True
    
    >>> _fnmatch_list("foo.PNG", ["*.png"])
    True

    >>> _fnmatch_list("foo.jpg", ["*.bar"])
    False
    """
    for filter in filter_list:
        if fnmatch(item.lower(), filter.lower()):
            return True
    return False


def _split_suffix(filename, suffix_list):
    """
    >>> _split_suffix("picture_no.jpg", ["_foo","_bar"])
    False

    >>> _split_suffix("picture_web.jpg", ["_web"])
    'picture'
    """
    name = os.path.splitext(filename)[0]
    for suffix in suffix_list:
        if name.endswith(suffix):
            cut_pos = len(suffix)
            cut_filename = name[:-cut_pos]
            return cut_filename
    return False


#------------------------------------------------------------------------------


class Gallery(BaseFilesystemBrowser):
    def __init__(self, config, *args, **kwargs):
#        # use unauthorized signs from preferences
#        pref_form = GalleryPrefForm()
#        preferences = pref_form.get_preferences()
#        unauthorized_signs = preferences["unauthorized_signs"]
#        kwargs["unauthorized_signs"] = unauthorized_signs

        super(Gallery, self).__init__(*args, **kwargs)

        # Galleries are only allowed in STATIC_ROOT
        static_root = add_slash(settings.STATIC_ROOT)
        self.check_path(static_root, self.abs_path)

        self.config = config
        self.static_base_url = posixpath.normpath(posixpath.join(settings.STATIC_URL, config.path, self.rel_url))

        dirs, pictures, thumbs = self.read_dir(self.abs_path)

        self.dir_info = self.build_dir_info(dirs)
        self.picture_info = self.build_picture_info(pictures, thumbs)

    def read_dir(self, path):
        pictures = []
        thumbs = {}
        dirs = []
        for item in os.listdir(path):
            if _fnmatch_list(item, self.config.diritem_blacklist):
                # Skip file/direcotry
                continue

            abs_item_path = os.path.join(path, item)
            if os.path.isdir(abs_item_path):
                dirs.append(item)
            elif os.path.isfile(abs_item_path):
                if not _fnmatch_list(item, self.config.filename_whitelist):
                    # Skip files witch are not in whitelist
                    continue

                cut_filename = _split_suffix(item, self.config.thumb_suffix_marker)
                if cut_filename:
                    thumbs[cut_filename] = item
                else:
                    pictures.append(item)

        pictures.sort()
        dirs.sort()

        return dirs, pictures, thumbs

    def build_dir_info(self, dirs):
        if self.rel_url not in ("", "/"):
            dirs.insert(0, "..")

        dir_info = []
        for dir in dirs:
            abs_sub_dir = os.path.join(self.abs_path, dir)
            sub_pictures = self.read_dir(abs_sub_dir)[1]

            dir_info.append({
                "verbose_name": dir.replace("_", " "),
                "href": "%s/" % posixpath.join(self.request.path, dir),
                "pic_count": len(sub_pictures),
            })

        return dir_info

    def make_url(self, part):
        return posixpath.normpath(posixpath.join(self.static_base_url, part))

    def build_picture_info(self, pictures, thumbs):
        picture_info = []
        for picture in pictures:
            cut_filename = _split_suffix(picture, self.config.filename_suffix_filter)
            if not cut_filename:
                cut_filename = os.path.splitext(picture)[0]

            info = {
                "href": self.make_url(picture),
                "verbose_name": cut_filename.replace("_", " "),
            }

            if cut_filename in thumbs:
                info["thumb_href"] = self.make_url(thumbs[cut_filename])
            else:
                info["thumb_href"] = self.make_url(picture)
                info["thumb_width"] = self.config.default_thumb_width
                info["thumb_height"] = self.config.default_thumb_height

            picture_info.append(info)
        return picture_info

    def render(self):
        context = {
            "a_rel_info": self.breadcrumbs[-1]["name"],
            "rel_path": self.rel_path,
            "dir_info": self.dir_info,
            "picture_info": self.picture_info,
            "breadcrumbs": self.breadcrumbs,
        }

        # ajax and non ajax response
        return render_pylucid_response(self.request, self.config.template, context,
            context_instance=RequestContext(self.request)
        )


def gallery(request, rest_url=""):
    pagetree = request.PYLUCID.pagetree
    try:
        config = GalleryModel.objects.get(pagetree=pagetree)
    except GalleryModel.DoesNotExist, err:
        if request.user.has_perm("gallery.change_gallerymodel"):
            messages.info(request,
                _("Gallery entry for page: %s doesn't exist, please create it.") % pagetree.get_absolute_url()
            )
            return HttpResponseRedirect(reverse("admin:gallery_gallerymodel_add"))
        else:
            messages.warning(request, _("Gallery is deactivated, yet. Come back later."))
            if not pagetree.parent:
                parent_url = "/"
            else:
                parent_url = pagetree.parent.get_absolute_url()
            return HttpResponseRedirect(parent_url)

    rel_base_path = config.path
    base_url = request.PYLUCID.pagemeta.get_absolute_url()
    absolute_path = os.path.normpath(os.path.join(settings.STATIC_ROOT, rel_base_path))

    try:
        gallery = Gallery(config, request, absolute_path, base_url, rest_url)
    except FilemanagerError, err:
        has_change_perm = request.user.has_perm("gallery.change_gallerymodel")
        if settings.DEBUG or has_change_perm:
            raise

        LogEntry.objects.log_action(
            app_label="pylucid_plugin.gallery", action="build gallery", message="%s" % err
        )
        raise Http404("Gallery error.")


    if not request.is_ajax():
        # FIXME: In Ajax request, only the page_content would be replaced, not the
        # breadcrumb links :(
        context = request.PYLUCID.context
        try:
            breadcrumb_context_middlewares = request.PYLUCID.context_middlewares["breadcrumb"]
        except KeyError:
            # e.g.: no breadcrumbs in template
            pass
        else:
            for breadcrumb_info in gallery.breadcrumbs[1:]:
                breadcrumb_context_middlewares.add_link(**breadcrumb_info)

        if gallery.rel_url:
            # Add sub path to permalink
            request.PYLUCID.context["page_permalink"] += "/%s/" % gallery.rel_url

    return gallery.render()





if __name__ == "__main__":
    import doctest
    print doctest.testmod(
#        verbose=True
        verbose=False
    )
