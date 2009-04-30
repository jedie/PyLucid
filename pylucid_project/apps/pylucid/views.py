

from django.conf import settings
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




def existing_lang(request, url_path):
    """
    List all available languages.
    """   
    try:
        pagetree, prefix_url, rest_url = PageTree.objects.get_page_from_url(url_path)
    except PageTree.DoesNotExist, err:
        return HttpResponseNotFound("<h1>Page not found</h1><h2>%s</h2>" % err)
    
    # Get the default language from system preferences
    system_preferences = SystemPreferencesForm().get_preferences()  
    lang_code = system_preferences["lang_code"]
    default_lang = Language.objects.get(code=lang_code)

    # Get the pagecontent instance in default language, for building the page
    pagecontent = PageContent.objects.get(lang=default_lang,page=pagetree)
    
    # Get all page content for this pagetree entry
    pages = PageContent.objects.all().filter(page=pagetree)
    
    request.PYLUCID = RequestObjects
    request.PYLUCID.pagetree = pagetree
    request.PYLUCID.pagecontent = pagecontent
    
    template_name = pagetree.design.template

    context = RequestContext(request, {
        "pagetree": pagetree,
        "pagecontent": pagecontent,
        "template_name": template_name,
        "pages": pages,
    })    
    return render_to_response('pylucid/existing_lang.html', context)


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



class RequestObjects(object):
    pass

def _render_page(request, pagetree, pagecontent):
    # Add some pylucid objects for the plugins on the request object
    request.PYLUCID = RequestObjects
    request.PYLUCID.pagetree = pagetree
    request.PYLUCID.pagecontent = pagecontent
    
    context = RequestContext(request, {
        "pagetree": pagetree,
        "pagecontent": pagecontent,
    })
    
    raw_html_content = apply_markup(pagecontent, request.page_msg)
    
    from django.template import Context, Template
    t = Template(raw_html_content)
    c = Context(context, context)
    html_content = t.render(c)
    
    template = pagetree.design.template
    
    context["html_content"] = html_content
    return render_to_response(template, context)


def resolve_url(request, lang_code, url_path):
    """ get a page """

    try:
        page, prefix_url, rest_url = PageTree.objects.get_page_from_url(url_path)
    except PageTree.DoesNotExist, err:
        return HttpResponseNotFound("<h1>Page not found</h1><h2>%s</h2>" % err)

    if page.type == PageTree.PLUGIN_TYPE:
        return _call_plugin(request, page, lang_code, prefix_url, rest_url)

    def lang_error(msg):
        """ send user a message and redirect to the existing lang. pagelist """
        # Leave a messages for the next page
        request.page_msg.red(msg)
        # redirect to the existing language page
        new_url = reverse('PyLucid-existing_lang', kwargs={"url_path":url_path})
        return HttpResponseRedirect(new_url)

    try:
        lang = Language.objects.get(code=lang_code)
    except Language.DoesNotExist:
        return lang_error("The language '%s' doesn't exist." % lang_code)
    
    try:
        content = PageContent.objects.get(lang=lang,page=page)
    except PageContent.DoesNotExist:
        return lang_error("The page doesn't exist in the requested language.")

    return _render_page(request, page, content)



