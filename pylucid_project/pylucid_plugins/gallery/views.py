# coding: utf-8


"""
    PyLucid gallery
    ~~~~~~~~~~~~~~~
    
    :copyleft: 2010-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from fnmatch import fnmatch
from glob import glob
import os
import posixpath

if __name__ == "__main__":
    # For doctest only
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"
    from django.conf import global_settings
    global_settings.SITE_ID = 1

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponseBadRequest
from django.template.context import RequestContext
from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.models import LogEntry
from pylucid_project.apps.pylucid.shortcuts import render_pylucid_response

from gallery.models import GalleryModel
from gallery.preference_forms import GalleryPrefForm


#------------------------------------------------------------------------------


def _fnmatch_list(item, filter_list):
    """
    >>> _fnmatch_list("foo.jpg", ["*.bar", "*.jpg"])
    True
    
    >>> _fnmatch_list("foo.jpg", ["*.bar"])
    False
    """
    for filter in filter_list:
        if fnmatch(item, filter):
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


class GalleryError(Exception):
    """
    for errors with a message to staff/admin users.
    e.g.: Gallery filesystem path doesn't exist anymore.
    """
    pass


class Gallery(object):
    def __init__(self, request, config, rest_url):
        self.request = request
        self.pagetree = self.request.PYLUCID.pagetree
        self.config = config

        self.gallery_base_url = self.request.PYLUCID.pagemeta.get_absolute_url()

        self.rel_path, self.rel_url = self.check_rest_url(rest_url)

        self.rel_base_path = self.config.path
        self.abs_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, self.rel_base_path, self.rel_path))

        is_dir = os.path.isdir(self.abs_path)
        is_in_root = self.abs_path.startswith(settings.MEDIA_ROOT)
        if not is_dir or not is_in_root:
            msg = _("Wrong path.")
            has_change_perm = request.user.has_perm("gallery.change_gallerymodel")
            if settings.DEBUG or has_change_perm:
                msg += " - path %r" % self.abs_path
                if not is_dir:
                    msg += " is not a directory."
                if not is_in_root:
                    msg += " is not in media root."
                if has_change_perm: # raise 404 in debug
                    raise GalleryError(msg)
            raise Http404(msg)

        self.abs_base_url = posixpath.normpath(posixpath.join(settings.MEDIA_URL, self.rel_base_path, self.rel_path))

        dirs, pictures, thumbs = self.read_dir(self.abs_path)

        self.dir_info = self.build_dir_info(dirs)
        self.picture_info = self.build_picture_info(pictures, thumbs)

        self.breadcrumbs = self.build_breadcrumbs()

    def build_breadcrumbs(self):
        parts = ""
        url = self.gallery_base_url
        breadcrumbs = [{
            "name": _("index"),
            "title": _("goto 'index'"),
            "url": url
        }]
        rel_url = self.rel_url.strip("/")
        if not rel_url:
            return breadcrumbs

        for url_part in rel_url.split("/"):
            url += "%s/" % url_part
            parts += "%s/" % url_part
            breadcrumbs.append({
                "name": url_part,
                "title": _("goto '%s'") % parts,
                "url": url
            })
        return breadcrumbs

    def make_url(self, part):
        return posixpath.normpath(posixpath.join(self.abs_base_url, part))

    def check_rest_url(self, rest_url):
        if rest_url == "":
            return ("", "")

        pref_form = GalleryPrefForm()
        preferences = pref_form.get_preferences()
        unauthorized_signs = preferences["unauthorized_signs"]
        assert isinstance(unauthorized_signs, (list, tuple))
        for sign in unauthorized_signs:
            if sign and sign in rest_url:
                msg1 = "unauthorized sign"
                msg = "'%s' in '%s'" % (sign, rest_url)
                LogEntry.objects.log_action(
                    app_label="pylucid_plugin.gallery", action=msg1, message=msg
                )
                msg404 = "bad path"
                if settings.DEBUG or self.request.user.is_staff:
                    msg404 += " - %s: %s" % (msg1, msg)
                raise Http404(msg404)

        rel_path = os.path.normpath(rest_url)
        rel_url = posixpath.normpath(rel_path)
        return rel_path, rel_url

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
        if self.rel_path != "":
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

    try:
        gallery = Gallery(request, config, rest_url)
    except GalleryError, err:
        messages.error(request, "Gallery error: %s" % err)
        return HttpResponseRedirect(reverse("admin:gallery_gallerymodel_change", args=(config.id,)))

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
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
