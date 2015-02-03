# coding: utf-8


"""
    PyLucid resolve url
    ~~~~~~~~~~~~~~~~~~~

    :copyleft: 2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from xml.sax.saxutils import escape

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404, HttpResponsePermanentRedirect
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.models.pagetree import PageTree
from pylucid_project.apps.pylucid.models.language import Language
from pylucid_project.apps.pylucid.models.pluginpage import PluginPage


def get_page_from_url(request, url_slugs):
    """
    returns a tuple the page tree instance from the given url_slugs
    """
    if not request.user.is_superuser:
        user_groups = request.user.groups.all()

    assert "?" not in url_slugs

    def _raise404(debug_msg):
        msg = _("Page not found")
        if settings.DEBUG or request.user.is_staff:
            msg += " url path: %r (%s)" % (url_slugs, debug_msg)
        raise Http404(msg)

    path = url_slugs.strip("/").split("/")
    page = None
    for no, page_slug in enumerate(path):
        if slugify(page_slug) != page_slug.lower():
            _raise404("url part %r is not slugify" % page_slug)

        try:
            page = PageTree.on_site.get(parent=page, slug=page_slug)
        except PageTree.DoesNotExist, err:
            _raise404("wrong slug %r: %s" % (page_slug, err))

        page_view_group = page.permitViewGroup

        # Check permissions only for PageTree
        # Note: PageMeta.permitViewGroup would be checked in self.get_pagemeta()
        # TODO: Check this in unittests!
        if request.user.is_anonymous():
            # Anonymous user are in no user group
            if page_view_group != None:
                msg = "Permission deny"
                if settings.DEBUG:
                    msg += " (url part: %s)" % escape(page_slug)
                raise PermissionDenied(msg)
        elif not request.user.is_superuser: # Superuser can see everything ;)
            if (page_view_group != None) and (page_view_group not in user_groups):
                msg = "Permission deny"
                if settings.DEBUG:
                    msg += " (not in view group %r, url part: %r)" % (page_view_group, escape(page_slug))
                raise PermissionDenied(msg)

        if page.page_type == PageTree.PLUGIN_TYPE:
            # It's a plugin
            prefix_url = "/".join(path[:no + 1])
            rest_url = "/".join(path[no + 1:])
#                if not rest_url.endswith("/"):
#                    rest_url += "/"
            return (page, prefix_url, rest_url)

    return (page, None, None)


def resolve_pagetree_url(request):
    """
    resolve the request.path and add PyLucid objects to the request object
    
    Note:
        request.PYLUCID created in PyLucidMiddleware
        
    expose theses Objects:
        request.PYLUCID.pagetree - PageTree instance
        request.PYLUCID.path_info - hold some path information
        request.PYLUCID.pagemeta
        request.PYLUCID.pluginpage - PluginPage instance, but only if current page is a PluginPage
        request.PYLUCID.updateinfo_object
        request.PYLUCID.object2comment - The Object used to attach a pylucid_comment
    """

    path_info = request.PYLUCID.path_info # PathInfo instance

    raw_path = path_info.raw_path # request.path

    # We should always get a url with at least two parts, e.g.:
    # /en/page_slug/
    # /en/page/sub-page/
    # /page/sub-page/
    # All other possible urls (root url and root lang url) should
    # be catch by other views in urls.py
    assert raw_path != ""
    assert "/" in raw_path

    url_lang_code, url_slugs = raw_path.strip("/").split("/", 1)

    if Language.objects.is_language_code(url_lang_code) != True:
        # It's not a valid language code -> redirect with added language code
        # e.g.:
        # lang code is a page slug
        # lang code is wrong or not existing
        try:
            # Try if lang code is a page slug
            pagetree, prefix_url, rest_url = get_page_from_url(request, raw_path)
        except Http404, err:
            # Maybe lang code is wrong or not existing -> try the rest slugs
            pagetree, prefix_url, rest_url = get_page_from_url(request, url_slugs)

        pagemeta = PageTree.objects.get_pagemeta(request, pagetree,
#             show_lang_errors=True
            show_lang_errors=False
        )
        new_url = pagemeta.get_absolute_url()
        return HttpResponsePermanentRedirect(new_url)
#         if _lang_code_is_pagetree(request, url_lang_code):
#             # url_lang_code doesn't contain a language code, it's a pagetree slug
#             new_url = "%s/%s" % (url_lang_code, url_path)
#             return _i18n_redirect(request, url_path=new_url)

    path_info.set_url_lang_info(url_lang_code, url_slugs)

    pagetree, prefix_url, rest_url = get_page_from_url(request, url_slugs)

    request.PYLUCID.pagetree = pagetree
    path_info.set_plugin_url_info(prefix_url, rest_url)

    pagemeta = PageTree.objects.get_pagemeta(request, pagetree,
        show_lang_errors=True
#         show_lang_errors=False
    )
    request.PYLUCID.pagemeta = pagemeta
    # url = pagemeta.get_absolute_url()

    # Changeable by plugin/get view or will be removed with PageContent instance
    request.PYLUCID.updateinfo_object = pagemeta

    # should be changed in plugins, e.g.: details views in blog, lexicon plugins
    request.PYLUCID.object2comment = pagemeta

    path_info.is_plugin_page = pagetree.page_type == PageTree.PLUGIN_TYPE
    if path_info.is_plugin_page:
        # Current page is a PluginPage
        pluginpage = PluginPage.objects.get(pagetree=pagetree)
        request.PYLUCID.pluginpage = pluginpage
