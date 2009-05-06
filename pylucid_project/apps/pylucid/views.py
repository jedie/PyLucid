# coding: utf-8

from django import http
from django.conf import settings
from django.template import loader, RequestContext, Context, Template

from pylucid.system import pylucid_plugin, i18n, pylucid_objects
from pylucid.markup.converter import apply_markup

from pylucid.models import PageTree, PageContent, EditableHtmlHeadFile


# use the undocumented django function to add the "lucidTag" to the tag library.
# see ./pylucid/defaulttags/__init__.py
from django.template import add_to_builtins
add_to_builtins('pylucid_project.apps.pylucid.defaulttags')


#_____________________________________________________________________________
# helper functions

def _prepage_request(request):
    """
    shared function for serval views.
    * add PyLucid request objects
    * setup i18n language settings
    """
    # Add PyLucid objects to the request object
    request.PYLUCID = pylucid_objects.PyLucidRequestObjects()
    # Add the Language model entry to request.PYLUCID.lang_entry
    i18n.setup_language(request)


def _get_page_content(request):
    """
    Returns the PageContent instance for the given pagetree:
    Try in client favored language, if not exist...
    ...try in default language set in the system preferences, if not exist...
    ...raise http.Http404()
    """
    pagetree = request.PYLUCID.pagetree
    
    queryset = PageContent.objects.all().filter(page=pagetree)
    try:
        return queryset.get(lang=request.PYLUCID.lang_entry)
    except PageContent.DoesNotExist:
        if settings.DEBUG or settings.PYLUCID.I18N_DEBUG:
            request.page_msg.error(
                "Page %r doesn't exist in language %r." % (pagetree, request.PYLUCID.lang_entry)
            )
            request.page_msg("Use default language from system preferences.")
            
        # Get the PageContent entry in the system default language
        i18n.activate_lang(request, request.PYLUCID.default_lang_code, from_info="system preferences")
        try:
            return queryset.get(lang=request.PYLUCID.lang_entry)
        except PageContent.DoesNotExist, err:
            raise http.Http404(
                "<h1>Page '%s' does not exist in default language '%s'.</h1>"
                "<p>Original error was: <strong>%s</strong>" % (
                    pagetree.slug, request.PYLUCID.lang_entry.code, err
                )
            )

def _render_string_template(template, context):
    """ render the given template string """
    t = Template(template)
    c = Context(context)
    return t.render(c)

   
def _render_template(request, page_content):
    context = request.PYLUCID.context
    page_template = request.PYLUCID.page_template
    context["page_content"] = page_content
    complete_page = _render_string_template(page_template, context)
       
    response = http.HttpResponse(complete_page, mimetype="text/html")
    response = pylucid_plugin.context_middleware_response(request, response)
    return response
    

def _render_page(request, pagetree, prefix_url=None, rest_url=None):
    """ render a cms page """   
    request.PYLUCID.pagetree = pagetree
    
    # Get template content and add it to PyLucid objects
    template_name = pagetree.design.template
    page_template, origin = loader.find_template_source(template_name)
    request.PYLUCID.page_template = page_template
    
    # Get the pagemeta instance for the current pagetree and language
    pagemeta = PageTree.objects.get_pagemeta(request)
    
    # Create initial context object
    context = RequestContext(request, {
        "pagetree": pagetree,
        "template_name": template_name,
        "page_title": pagemeta.title_or_slug(),
        "page_keywords": pagemeta.keywords,
        "page_description": pagemeta.description,
    })
    request.PYLUCID.context = context
    
    # Get all plugin context middlewares from the template and add them to the context
    pylucid_plugin.context_middleware_request(request)
    
    pagecontent = _get_page_content(request)        
    request.PYLUCID.pagecontent = pagecontent    
    context["page_content"] = pagecontent
    
    # call a pylucid plugin "html get view", if exist
    get_view_response = pylucid_plugin.call_get_views(request)
    if get_view_response != None:
        # Use plugin response      
        assert(isinstance(get_view_response, http.HttpResponse),
            "pylucid plugins must return a http.HttpResponse instance or None!"
        )
        response = pylucid_plugin.context_middleware_response(request, get_view_response)
        return response
#        if get_view_response.status_code == 200:
#            # Plugin replace the page content
#            return _render_template(request, page_content=get_view_response.content)
#        else:
#            # Plugin has return a response object, but not a normal content, it's a redirect, not found etc.
#            return get_view_response
        
    # call page plugin, if current page is a plugin page
    page_plugin_response = None
    if pagetree.type == PageTree.PLUGIN_TYPE:
        # The current PageTree entry is a plugin page
        page_plugin_response = pylucid_plugin.call_plugin(request, prefix_url, rest_url)
        assert(isinstance(page_plugin_response, http.HttpResponse),
            "pylucid plugins must return a http.HttpResponse instance or None!"
        )
        response = pylucid_plugin.context_middleware_response(request, page_plugin_response)
        return response
#        if page_plugin_response.status_code == 200:
#            # Plugin replace the page content
#            return _render_template(request, page_content=page_plugin_response.content)
#        else:
#            # Plugin has return a response object, but not a normal content, it's a redirect, not found etc.
#            return page_plugin_response
        
    
    # Plugin has not return a response object -> use the normal page content
    raw_html_content = apply_markup(request.PYLUCID.pagecontent, request.page_msg)
    
    html_content = _render_string_template(raw_html_content, context)

    return _render_template(request, page_content=html_content)








#_____________________________________________________________________________
# view functions


def send_head_file(request, filename):
    """
    Sending a headfile
    only a fall-back method if the file can't be stored into the media path
    """
    try:
        headfile = EditableHtmlHeadFile.objects.get(filename=filename)
    except EditableHtmlHeadFile.DoesNotExist:
        if settings.DEBUG:
            request.page_msg.error("Headfile %r not found!" % filename)
        raise http.Http404
    
    mimetype = headfile.get_mimetype()
    content = headfile.content
    
    return http.HttpResponse(content, mimetype=mimetype)


def root_page(request):
    """ render the first root page in system default language """
    _prepage_request(request)
    
    # Get the first PageTree entry
    pagetree = PageTree.objects.all().filter(parent=None).order_by("position")[0]

    return _render_page(request, pagetree)


def cms_page(request, url_path):
    """ render cms page view """
    _prepage_request(request)
    
    try:
        pagetree, prefix_url, rest_url = PageTree.objects.get_page_from_url(url_path)
    except PageTree.DoesNotExist, err:
        return http.HttpResponseNotFound("<h1>Page not found</h1><h2>%s</h2>" % err)
    
    return _render_page(request, pagetree, prefix_url, rest_url)





