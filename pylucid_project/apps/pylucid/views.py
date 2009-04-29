

from django.conf import settings
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseNotFound, HttpResponseRedirect

from pylucid.markup.converter import apply_markup
from pylucid.models import PageTree, Language, PageContent, EditableHtmlHeadFile


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
    request.user.message_set.create(message="root_page view - Test with request.user.message_set.create")
    request.page_msg("root_page view - Test with request.page_msg")
    
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



EXISTING_LANG_MSG = "message for existing lang page"

def existing_lang(request, url_path):
    result = "TODO: existing lang page for: %s" % url_path
    
    if EXISTING_LANG_MSG in request.session:
        result += request.session.pop(EXISTING_LANG_MSG)
        
    return HttpResponse(result)

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
        page, rest_url = PageTree.objects.get_page_from_url(url_path)
    except PageTree.DoesNotExist, err:
        return HttpResponseNotFound("<h1>Page not found</h1><h2>%s</h2>" % err)

    if page.type == PageTree.PLUGIN_TYPE:
        return HttpResponse("TODO: Plugin url: %r" % rest_url)

    def lang_error(msg):
        """ send user a message and redirect to the existing lang. pagelist """
        #request.user.message_set.create(message=msg) <<< works not for anonymous user, yet.
        # work-a-round since http://code.djangoproject.com/ticket/4604 lands:
        request.session[EXISTING_LANG_MSG] = msg
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

    return HttpResponse("lang: %r path: %r resolved_id: %r\n\n%r" % (lang_code, url_path, str(page.id),content.content))




#def get_page(request, page_id):
#    page = Page08.objects.get(id=page_id)
#    context = {
#        "page": page,
#    }
#    return render_to_response('pylucid/test.html', context)
