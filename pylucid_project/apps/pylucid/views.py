# coding: utf-8

from django import http
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import loader, RequestContext, Context, Template

from django_tools.template import render

from pylucid.system import pylucid_plugin, i18n, pylucid_objects
from pylucid.markup.converter import apply_markup
from pylucid.models import PageTree, PageContent, ColorScheme, EditableHtmlHeadFile, Language


# use the undocumented django function to add the "lucidTag" to the tag library.
# see ./pylucid/defaulttags/__init__.py
from django.template import add_to_builtins
add_to_builtins('pylucid_project.apps.pylucid.defaulttags')


#_____________________________________________________________________________
# helper functions

def _get_page_content(request):
    """
    Returns the PageContent instance for the current pagetree:
    Try in client favored language, if not exist...
    ...try in default language set in the system preferences, if not exist...
    ...raise http.Http404()
    """
    # current pagetree instance:
    pagetree = request.PYLUCID.pagetree
    # client favored Language instance:
    lang_entry = request.PYLUCID.lang_entry
    # default Language instance set in system preferences:
    default_lang_entry = request.PYLUCID.default_lang_entry
    
    try:
        pagecontent = PageTree.objects.get_pagecontent(request)
    except PageContent.DoesNotExist, err:
        raise http.Http404(
            "Page '%s' does not exist in default language '%s'.\n"
            "Original error was: %s" % (
                pagetree.slug, default_lang_entry.code, err
            )
        )
    
    if (settings.DEBUG or settings.PYLUCID.I18N_DEBUG) and (pagecontent.lang != lang_entry):
        request.page_msg.error(
            "Page '%s' doesn't exist in client favored language '%s', use '%s' entry." % (
                pagetree.slug, lang_entry.code, pagecontent.lang.code
            )
        )
        
    return pagecontent

   
def _render_template(request, page_content):
    context = request.PYLUCID.context
    page_template = request.PYLUCID.page_template
    context["page_content"] = page_content
    complete_page = render.render_string_template(page_template, context)
       
    response = http.HttpResponse(complete_page, mimetype="text/html")
    response["content-language"] = context["page_language"]
    response = pylucid_plugin.context_middleware_response(request, response)
    return response


def _apply_context_middleware(request, response):
    """
    Before we "send" the response back to the client, we replace all existing
    context_middleware tags.
    """
    response = pylucid_plugin.context_middleware_response(request, response)
    return response


def _render_page(request, pagetree, prefix_url=None, rest_url=None):
    """ render a cms page """   
    request.PYLUCID.pagetree = pagetree

    # Get the pagemeta instance for the current pagetree and language
    pagemeta = PageTree.objects.get_pagemeta(request)
    request.PYLUCID.pagemeta = pagemeta
    
    # Get template content and add it to PyLucid objects
    template_name = pagetree.design.template
    page_template, origin = loader.find_template_source(template_name)
    request.PYLUCID.page_template = page_template
    
    # Create initial context object
    context = RequestContext(request, {
        "pagetree": pagetree,
        "template_name": template_name,
        "page_title": pagemeta.title_or_slug(),
        "page_keywords": pagemeta.keywords,
        "page_description": pagemeta.description,
        "page_language": pagemeta.lang.code,
    })
    request.PYLUCID.context = context
    
    # Get all plugin context middlewares from the template and add them to the context
    pylucid_plugin.context_middleware_request(request)
    
    # call page plugin, if current page is a plugin page
    page_plugin_response = None
    if pagetree.type == PageTree.PLUGIN_TYPE:
        # The current PageTree entry is a plugin page
        page_plugin_response = pylucid_plugin.call_plugin(request, prefix_url, rest_url)

        if isinstance(page_plugin_response, http.HttpResponse):
            # Plugin would be build the complete html page
            response = _apply_context_middleware(request, page_plugin_response)
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
        context["page_content"] = pagecontent_instance.content
        updateinfo_object = pagecontent_instance

    # Add UpdateInfoBaseModel meta data from PageContent/PageMeta instance into context
    # FIXME: Do this erlear: So A plugin page can change the values!
    for itemname in ("createby", "lastupdateby", "createtime", "lastupdatetime"):
        context["page_%s" % itemname] = getattr(updateinfo_object, itemname)        
    
    # call a pylucid plugin "html get view", if exist
    get_view_response = pylucid_plugin.call_get_views(request)
    if get_view_response != None:
        # Use plugin response      
        assert(isinstance(get_view_response, http.HttpResponse),
            "pylucid plugins must return a http.HttpResponse instance or None!"
        )
        if isinstance(get_view_response, http.HttpResponse):
            # Plugin would be build the complete html page
            response = _apply_context_middleware(request, get_view_response)
            return response
        
        assert isinstance(get_view_response, basestring), \
            "Plugin get view must return None, HttpResponse or a basestring!"
        
        # Plugin replace the page content
        context["page_content"] = get_view_response
    
    if page_plugin_response == None and get_view_response == None:
        # No Plugin has changed the PageContent -> apply markup on PageContent
        raw_html_content = apply_markup(pagecontent_instance, request.page_msg)
    else:
        raw_html_content = context["page_content"]
    
    html_content = render.render_string_template(raw_html_content, context)

    response = _render_template(request, page_content=html_content)
    
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



def _add_pylucid_request_objects(request):
    """ Add PyLucid objects to the request object """
    request.PYLUCID = pylucid_objects.PyLucidRequestObjects()


def _prepage_request(request, lang_entry):
    """
    shared function for serval views.
    * 
    """
    # setup i18n language settings
    i18n.setup_language(request, lang_entry)

#_____________________________________________________________________________
# root_page + lang_root_page views:

def _render_root_page(request):
    """ render the root page, used in root_page and lang_root_page views """
    # Get the first PageTree entry
    pagetree = PageTree.objects.get_root_page()
    
    return _render_page(request, pagetree)


def root_page(request):
    """ render the first root page in system default language """
    _add_pylucid_request_objects(request)
    
    # activate language via auto detection
    i18n.activate_auto_language(request)
    
    return _render_root_page(request)


def lang_root_page(request, url_lang_code):
    """ url with lang code but no page slug """
    _add_pylucid_request_objects(request)
    
    try:
        lang_entry = Language.objects.get(code=url_lang_code)
    except Language.DoesNotExist:
        request.page_msg.error("Language '%s' doesn't exist." % url_lang_code)
        # redirect to "/"
        return http.HttpResponseRedirect("/")
    
    # activate i18n
    i18n.activate_language(request, lang_entry, save=True)
    
    return _render_root_page(request)

#-----------------------------------------------------------------------------

def _i18n_redirect(request, url_path):
    """ Redirect to a url with the default language code. """
    # activate language via auto detection
    i18n.activate_auto_language(request) 
    
    # Check only, if url_path is right (if there exist a pagetree object)
    # otherwise -> 404 would be raised
    _get_pagetree(url_path)
    
    lang_code = request.LANGUAGE_CODE
    url = reverse('PyLucid-resolve_url', kwargs={'url_lang_code': lang_code, 'url_path': url_path})
    
    # redirect to url with lang_code
    return http.HttpResponseRedirect(url)


def _get_pagetree(url_path):
    try:
        return PageTree.objects.get_page_from_url(url_path)
    except PageTree.DoesNotExist, err:
        raise http.Http404("<h1>Page not found</h1><h2>%s</h2>" % err)

def resolve_url(request, url_lang_code, url_path):
    """ url with lang_code and sub page path """
    _add_pylucid_request_objects(request)
    
    try:
        lang_entry = Language.objects.get(code=url_lang_code)
    except Language.DoesNotExist:
        request.page_msg.error("Language '%s' doesn't exist." % url_lang_code)
        # redirect to a url with the default language code.
        return _i18n_redirect(request, url_path)
    
    # activate i18n
    i18n.activate_language(request, lang_entry, save=True)
    
    pagetree, prefix_url, rest_url = _get_pagetree(url_path)
    
    return _render_page(request, pagetree, prefix_url, rest_url)

    
def page_without_lang(request, url_path):
    """
    url with sub page path, but without a lang_code part
    We redirect to a url with language code.
    """
    _add_pylucid_request_objects(request)
    
    # redirect to a url with the default language code.
    return _i18n_redirect(request, url_path)


    






