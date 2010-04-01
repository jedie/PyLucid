# coding: utf-8

from django import http
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import loader, RequestContext
from django.utils.translation import ugettext as _

from django_tools.template import render

from pylucid_project.system.pylucid_plugins import PYLUCID_PLUGINS

from pylucid_project.apps.pylucid.markup.converter import apply_markup
from pylucid_project.apps.pylucid.signals import pre_render_global_template
from pylucid_project.apps.pylucid.system import pylucid_plugin, i18n
from pylucid_project.apps.pylucid.models import PageTree, PageMeta, PageContent, PluginPage, ColorScheme, \
                                                                    EditableHtmlHeadFile, Language


#_____________________________________________________________________________
# helper functions

def _get_page_content(request):
    """
    Returns the PageContent instance for the current pagetree:
    Try in client favored language, if not exist...
    ...try in default language set in the system preferences, if not exist...
    ...raise http.Http404()
    """
    pagetree = request.PYLUCID.pagetree # current PageTree instance
    pagemeta = request.PYLUCID.pagemeta # current PageMeta instance

    # client favored Language instance:
    lang_entry = request.PYLUCID.current_language
    # default Language instance set in system preferences:
    default_lang_entry = Language.objects.get_or_create_default(request)

    try:
        pagecontent = PageContent.objects.get(pagemeta=pagemeta)
    except PageContent.DoesNotExist, err:
        raise http.Http404(
            "Page '%s' does not exist in default language '%s'.\n"
            "Original error was: %s" % (
                pagetree.slug, default_lang_entry.code, err
            )
        )

    return pagecontent




def _apply_context_middleware(request, response):
    """
    Before we "send" the response back to the client, we replace all existing
    context_middleware tags.
    """
    response = pylucid_plugin.context_middleware_response(request, response)
    return response


def _render_page(request, pagetree, url_lang_code, prefix_url=None, rest_url=None):
    """ render a cms page """
    request.PYLUCID.pagetree = pagetree

    is_plugin_page = pagetree.page_type == PageTree.PLUGIN_TYPE

    # Get the pagemeta instance for the current pagetree and language
    try:
        pagemeta = PageTree.objects.get_pagemeta(request, pagetree, show_lang_errors=True)
    except PageMeta.DoesNotExist, err:
        # Note: This should normaly never happen. Because all PageMeta must exist at least in system
        # default language. Also: The main_manu doesn't show links to not existing PageMeta entries!
        if settings.DEBUG or settings.PYLUCID.I18N_DEBUG:
            raise
            msg = (
                "PageMeta for %r doesn't exist in system default language: %r! Please create it!"
                " (Original error was: %r)"
            ) % (pagetree, Language.objects.get_or_create_default(request), err)
            request.page_msg.error(msg)
        else:
            msg = ""
        raise http.Http404("<h1>Page not found</h1><h2>%s</h2>" % msg)

    request.PYLUCID.pagemeta = pagemeta

    # Check the language code in the url, if exist
    if url_lang_code and (not is_plugin_page) and (url_lang_code.lower() != pagemeta.language.code.lower()):
        # The language code in the url is wrong. e.g.: The client followed a external url with was wrong.
        # Note: The main_manu doesn't show links to not existing PageMeta entries!

        # change only the lang code in the url:
        new_url = i18n.change_url(request, new_lang_code=pagemeta.language.code)

        if settings.DEBUG or settings.PYLUCID.I18N_DEBUG:
            request.page_msg.error(
                "Language code in url %r is wrong! Redirect to %r." % (url_lang_code, new_url)
            )
        # redirect the client to the right url
        return http.HttpResponsePermanentRedirect(new_url)

    # Create initial context object
    request.PYLUCID.context = context = RequestContext(request)

    # Add the page template content to the pylucid objects
    # Used to find context middleware plugins and in _render_template()
    template_name = context["template_name"] # Added in pylucid.context_processors
    page_template, origin = loader.find_template_source(template_name)
    request.PYLUCID.page_template = page_template

    # Get all plugin context middlewares from the template and add them to the context
    pylucid_plugin.context_middleware_request(request)

    # call a pylucid plugin "html get view", if exist
    get_view_replace_content = False
    get_view_response = PYLUCID_PLUGINS.call_get_views(request)
    if get_view_response is not None: # Use plugin response
        if isinstance(get_view_response, http.HttpResponse):
            # Plugin would be build the complete html page
            response = _apply_context_middleware(request, get_view_response)
            return response

        assert isinstance(get_view_response, basestring), (
            "Plugin get view must return None, HttpResponse or a basestring! (returned: %r)"
        ) % type(get_view_response)

        # Plugin replace the page content
        context["page_content"] = get_view_response
        get_view_replace_content = True

    # call page plugin, if current page is a plugin page
    page_plugin_response = None
    if get_view_replace_content == False and is_plugin_page:
        # The current PageTree entry is a plugin page

        # Add to global pylucid objects. Use e.g. in admin_menu plugin
        pluginpage = PluginPage.objects.get(pagetree=pagetree)
        request.PYLUCID.pluginpage = pluginpage

        page_plugin_response = pylucid_plugin.call_plugin(request, url_lang_code, prefix_url, rest_url)

        if isinstance(page_plugin_response, http.HttpResponse):
            # Plugin would be build the complete html page
            response = _apply_context_middleware(request, page_plugin_response)
            context["page_content"] = response.content
            return response
        elif page_plugin_response == None:
            raise RuntimeError(
                "PagePlugin has return None, but it must return a HttpResponse object or a basestring!"
            )
        # Plugin replace the page content
        context["page_content"] = page_plugin_response
        updateinfo_object = pagemeta
    else:
        # No PluginPage
        pagecontent_instance = _get_page_content(request)
        request.PYLUCID.pagecontent = pagecontent_instance
        if get_view_replace_content == False:
            # Use only PageContent if no get view will replace the content
            context["page_content"] = pagecontent_instance.content
        updateinfo_object = pagecontent_instance

    # Add UpdateInfoBaseModel meta data from PageContent/PageMeta instance into context
    # FIXME: Do this erlear: So A plugin page can change the values!
    for itemname in ("createby", "lastupdateby", "createtime", "lastupdatetime"):
        context["page_%s" % itemname] = getattr(updateinfo_object, itemname)

    if page_plugin_response == None and get_view_response == None:
        # No Plugin has changed the PageContent -> apply markup on PageContent
        context["page_content"] = apply_markup(
            pagecontent_instance.content, pagecontent_instance.markup, request.page_msg
        )

    # Render django tags in PageContent with the global context
    context["page_content"] = render.render_string_template(context["page_content"], context)

    pre_render_global_template.send(sender=None, request=request, page_template=page_template)

    # Render django tags in global template with global context
    complete_page = render.render_string_template(page_template, context)

    # create response object
    response = http.HttpResponse(complete_page, mimetype="text/html")
    response["content-language"] = context["page_language"]

    # replace/render pylucid plugin context middlewares
    response = _apply_context_middleware(request, response)
    return response








#_____________________________________________________________________________
# view functions

def send_head_file(request, filepath):
    """
    Sending a headfile
    only a fall-back method if the file can't be stored into the media path
    """
    if "ColorScheme" in request.GET:
        colorscheme_pk = request.GET["ColorScheme"]
        try:
            colorscheme = ColorScheme.objects.get(pk=colorscheme_pk)
        except ColorScheme.DoesNotExist:
            if settings.DEBUG:
                msg = "ColorScheme %r not found!" % colorscheme_pk
            else:
                msg = ""
            raise http.Http404(msg)

    try:
        headfile = EditableHtmlHeadFile.objects.get(filepath=filepath)
    except EditableHtmlHeadFile.DoesNotExist:
        if settings.DEBUG:
            msg = "Headfile %r not found!" % filepath
        else:
            msg = ""
        raise http.Http404(msg)

    if headfile.render:
        content = headfile.get_rendered(colorscheme)
    else:
        content = headfile.content

    mimetype = headfile.mimetype
    return http.HttpResponse(content, mimetype=mimetype)



def _prepage_request(request, lang_entry):
    """
    shared function for serval views.
    * 
    """
    # setup i18n language settings
    i18n.setup_language(request, lang_entry)

#_____________________________________________________________________________
# root_page + lang_root_page views:

def _render_root_page(request, url_lang_code=None):
    """ render the root page, used in root_page and lang_root_page views """
    user = request.user
    try:
        pagetree = PageTree.objects.get_root_page(user) # Get the first PageTree entry
    except PageTree.DoesNotExist, err:
        msg = _("There exist no pages items! Have you install PyLucid? At least you must create one page!")
        # TODO: Redirect to install page?
        request.page_msg.error(msg)
        return http.HttpResponseRedirect(reverse("admin:index"))

    return _render_page(request, pagetree, url_lang_code)


def root_page(request):
    """ render the first root page in system default language """
    # activate language via auto detection
    i18n.activate_auto_language(request)

    return _render_root_page(request)


def lang_root_page(request, url_lang_code):
    """ url with lang code but no page slug """
    # activate i18n
    i18n.activate_auto_language(request)

    return _render_root_page(request, url_lang_code)

#-----------------------------------------------------------------------------

def _i18n_redirect(request, url_path):
    """ Redirect to a url with the default language code. """
    # activate language via auto detection
    i18n.activate_auto_language(request)

    # Check only, if url_path is right (if there exist a pagetree object)
    # otherwise -> 404 would be raised
    _get_pagetree(request, url_path)

    lang_code = request.LANGUAGE_CODE
    url = reverse('PyLucid-resolve_url', kwargs={'url_lang_code': lang_code, 'url_path': url_path})

    if request.GET:
        # Add GET query string
        # We don't use request.GET.urlencode() here, because it can change the key positions
        full_path = request.get_full_path()
        get_string = full_path.split("?", 1)[1]
        url += "?" + get_string

    # redirect to url with lang_code
    return http.HttpResponseRedirect(url)


def _get_pagetree(request, url_path):
    try:
        return PageTree.objects.get_page_from_url(request, url_path)
    except PageTree.DoesNotExist, err:
        msg = _("Page not found")
        if settings.DEBUG or request.user.is_staff:
            msg += " url path: %r (%s)" % (url_path, err)
        raise http.Http404(msg)


def resolve_url(request, url_lang_code, url_path):
    """ url with lang_code and sub page path """
    # activate language via auto detection
    i18n.activate_auto_language(request)

    pagetree, prefix_url, rest_url = _get_pagetree(request, url_path)

    return _render_page(request, pagetree, url_lang_code, prefix_url, rest_url)


def page_without_lang(request, url_path):
    """
    url with sub page path, but without a lang_code part
    We redirect to a url with language code.
    """
    # redirect to a url with the default language code.
    return _i18n_redirect(request, url_path)


def permalink(request, page_id, url_rest=""):
    """ resolve a permalink and redirect to the real url. """
    # activate language via auto detection
    i18n.activate_auto_language(request)

    try:
        pagetree = PageTree.on_site.get(id=page_id)
    except PageTree.DoesNotExist, err:
        # TODO: Try to search with the additional url data (url_rest)
        msg = "Page not found"
        if settings.DEBUG:
            msg += " PageTree ID: %r (%s)" % (page_id, err)
        raise http.Http404(msg)

    pagemeta = PageTree.objects.get_pagemeta(request, pagetree, show_lang_errors=False)

    url = pagemeta.get_absolute_url()

    if pagetree.page_type == pagetree.PLUGIN_TYPE and url_rest and "/" in url_rest:
        # pass a permalink additional to the plugin, e.g.: blog entry detail view
        additional_url = url_rest.split("/", 1)[1]
        url += additional_url

    return http.HttpResponseRedirect(url)




