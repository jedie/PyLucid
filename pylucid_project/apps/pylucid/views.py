

from django.conf import settings
from django.utils import translation
from django.core import urlresolvers
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.importlib import import_module
from django.conf.urls.defaults import patterns, url
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseNotFound, HttpResponseRedirect

from pylucid.markup.converter import apply_markup
from pylucid.models import PageTree, Language, PageContent, PluginPage, EditableHtmlHeadFile
from pylucid.preference_forms import SystemPreferencesForm

# use the undocumented django function to add the "lucidTag" to the tag library.
# see ./pylucid/defaulttags/__init__.py
from django.template import add_to_builtins
add_to_builtins('pylucid_project.apps.pylucid.defaulttags')






def send_head_file(request, filename):
    """
    Sending a headfile
    only a fall-back method if the file can't be stored into the media path
    """
    try:
        headfile = EditableHtmlHeadFile.objects.get(filename=filename)
    except EditableHtmlHeadFile.DoesNotExist:
        raise Http404
    
    mimetype = headfile.get_mimetype()
    content = headfile.content
    
    return HttpResponse(content, mimetype=mimetype)



def root_page(request):
    """
    Display a root page with some usefull links
    XXX: Only for developing
    """
    request.PYLUCID = PyLucidRequestObjects()
    # Add the Language model entry to request.PYLUCID.lang_entry
    _setup_language(request)
    
    context = {
        "request": request, # FIXME: Can we add it throu a own context processors?
        "admin_url": "/%s/" % settings.ADMIN_URL_PREFIX,
    }
    return render_to_response('pylucid/root_page.html', context, context_instance=RequestContext(request))


def lang_root_page(request, lang_code):
    try:
        Language.objects.get(code=lang_code)
    except:
        return resolve_url(request,"",lang_code)

    return HttpResponse("root page for lang: %r" % lang_code)



class PyLucidRequestObjects(object):
    def __init__(self):
        self.system_preferences = SystemPreferencesForm().get_preferences()
        self.default_lang_code = self.system_preferences["lang_code"]
        self.default_lang_entry = Language.objects.get(code=self.default_lang_code)
        # objects witch will be set later:
        #self.lang_entry - The current language instance
 

def _activate_lang(request, lang_code, from_info, save=False):
    """
    Try to use the given lang_code. If not exist fall back to lang from system preferences.
    Add the Language model entry to request.PYLUCID.lang_entry
    """   
    try:
        lang_entry = Language.objects.get(code=lang_code)
    except Language.DoesNotExist:
        if settings.DEBUG or settings.PYLUCID.I18N_DEBUG:
            request.page_msg.red(
                "debug: Favored language %r (from: %s) doesn't exist." % (lang_code, from_info)
            )
        # The favored language doesn't exist -> use default lang from preferences
        lang_entry = request.PYLUCID.default_lang_entry
        lang_code = request.PYLUCID.default_lang_code
        if settings.PYLUCID.I18N_DEBUG:
            request.page_msg.green("Use default language %r (from preferences)" % lang_entry)
    else:
        if settings.PYLUCID.I18N_DEBUG:
            request.page_msg.green("Use language %r (from: %s)" % (lang_code, from_info))
        if save:
            # Save language in session for next requests
            if settings.PYLUCID.I18N_DEBUG:
                request.page_msg("Save lang code %r into request.session['django_language']" % lang_code)
            request.session["django_language"] = lang_code
      
    translation.activate(lang_code) # activate django i18n
    request.LANGUAGE_CODE = lang_code
    request.PYLUCID.lang_entry = lang_entry


def _setup_language(request):
    """
    Add the Language model entry to request.PYLUCID.lang_entry.
    Try to use GET parameter or fall back to django language information
    from django local middleware, see: http://docs.djangoproject.com/en/dev/topics/i18n/#id2 
    """
    if settings.PYLUCID.I18N_DEBUG:
        request.page_msg("settings.PYLUCID.I18N_DEBUG:")
        
        key = "HTTP_ACCEPT_LANGUAGE"
        request.page_msg("%s:" % key, request.META.get(key, '---'))
        
        key = settings.LANGUAGE_COOKIE_NAME
        request.page_msg("cookie %r:" % key, request.COOKIES.get(key, "---"))
        
        request.page_msg("session 'django_language':", request.session.get('django_language', "---"))
        
    
    # consider language in GET parameter
    key = settings.PYLUCID.FAVORED_LANG_GET_KEY
    lang_code = request.GET.get(key, False)
    if lang_code:
        _activate_lang(request, lang_code, from_info="request.GET['%s']" % key, save=True)
        return
        
    # Use language infomation from django locale middleware
    lang_code = request.LANGUAGE_CODE
    _activate_lang(request, lang_code, from_info="request.LANGUAGE_CODE")
    
    if settings.PYLUCID.I18N_DEBUG:
        request.page_msg("request.PYLUCID.default_lang_code:", request.PYLUCID.default_lang_code)
        request.page_msg("request.PYLUCID.default_lang_entry:", request.PYLUCID.default_lang_entry)
        request.page_msg("request.PYLUCID.lang_entry:", request.PYLUCID.lang_entry)


def _render_page(request):
    """ render a cms page """
    context = RequestContext(request, {
        "pagetree": request.PYLUCID.pagetree,
        "pagecontent": request.PYLUCID.pagecontent,
    })
    
    raw_html_content = apply_markup(request.PYLUCID.pagecontent, request.page_msg)
    
    from django.template import Context, Template
    t = Template(raw_html_content)
    c = Context(context, context)
    html_content = t.render(c)
    
    template = request.PYLUCID.pagetree.design.template
    
    context["html_content"] = html_content
    return render_to_response(template, context)



def cms_page(request, url_path):
    """
    List all available languages.
    """
    request.PYLUCID = PyLucidRequestObjects()
    
    try:
        pagetree, prefix_url, rest_url = PageTree.objects.get_page_from_url(url_path)
    except PageTree.DoesNotExist, err:
        return HttpResponseNotFound("<h1>Page not found</h1><h2>%s</h2>" % err)
    
    request.PYLUCID.pagetree = pagetree
    
    # Add the Language model entry to request.PYLUCID.lang_entry
    _setup_language(request)

    # Get the pagecontent instance, for building the page
    queryset = PageContent.objects.all().filter(page=pagetree)
    try:
        pagecontent = queryset.get(lang=request.PYLUCID.lang_entry)
    except PageContent.DoesNotExist:
        if settings.DEBUG or settings.PYLUCID.I18N_DEBUG:
            request.page_msg.red(
                "Page %r doesn't exist in language %r." % (pagetree, request.PYLUCID.lang_entry)
            )
            request.page_msg("Use default language from system preferences.")
        # Use language from system preferences to get the content entry
        _activate_lang(request, request.PYLUCID.default_lang_code, from_info="system preferences")
        pagecontent = queryset.get(lang=request.PYLUCID.lang_entry)
        
    request.PYLUCID.pagecontent = pagecontent
    
    # Get all page content for this pagetree entry
    pages = PageContent.objects.all().filter(page=pagetree)
    
    template_name = pagetree.design.template

    return _render_page(request)



class PluginGetResolver(object):
    def __init__(self, resolver):
        self.resolver = resolver
    def __call__(self, *args, **kwargs):
        return self.resolver

def _call_plugin(request, pagetree, lang_code, prefix_url, rest_url):
    """
    Call a plugin and return the response.
    """
    # Get the information witch django app would be used
    pluginpage = PluginPage.objects.get(page=pagetree)
    app_label = pluginpage.app_label
    plugin_urlconf_name = app_label + ".urls"
    
    # Get the urlpatterns from the plugin urls.py
    plugin_urlpatterns = import_module(plugin_urlconf_name).urlpatterns
    
    # build the url prefix
    prefix = "/".join(["^" + lang_code, prefix_url])
    if not prefix_url.endswith("/"):
        prefix += "/"

    # The used urlpatterns
    urlpatterns2 = patterns('', url(prefix, [plugin_urlpatterns]))
    
    # Append projects own url patterns, so the plugin can reverse url from them, too.
    current_urlpatterns = import_module(settings.ROOT_URLCONF).urlpatterns
    urlpatterns2 += current_urlpatterns
    
    # Make a own url resolver
    resolver = urlresolvers.RegexURLResolver(r'^/', urlpatterns2)
    
#    for key in resolver.reverse_dict:
#        print key, resolver.reverse_dict[key]

    # get the plugin view from the complete url
    resolve_url = request.path_info
    result = resolver.resolve(resolve_url)
    if result == None:
        raise urlresolvers.Resolver404, {'tried': resolver.url_patterns, 'path': rest_url}
    
    view_func, view_args, view_kwargs = result
    
    # Patch urlresolvers.get_resolver() function, so only our own resolver with urlpatterns2
    # is active in the plugin. So the plugin can build urls with normal django function and
    # this urls would be prefixed with the current PageTree url.
    old_get_resolver = urlresolvers.get_resolver
    urlresolvers.get_resolver = PluginGetResolver(resolver)
    
    # Add some pylucid objects for the plugins on the request object
    request.PYLUCID = RequestObjects
    request.PYLUCID.pagetree = pagetree
    
    #FIXME: Some plugins needs a "current pagecontent" object!
    #request.PYLUCID.pagecontent = 
    
    # Call the view
    response = view_func(request, *view_args, **view_kwargs)
    
    # restore the patched function
    urlresolvers.get_resolver = old_get_resolver
    
    return response












