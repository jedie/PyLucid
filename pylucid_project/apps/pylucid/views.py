

from django.conf import settings
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect


#from pylucid_project.apps.pylucid.models import Page08
from pylucid_project.apps.pylucid.models import *

# use the undocumented django function to add the "lucidTag" to the tag library.
# see ./pylucid/defaulttags/__init__.py
from django.template import add_to_builtins
add_to_builtins('pylucid_project.apps.pylucid.defaulttags')


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
    return HttpResponse("TODO: existing lang page for: %s" % url_path)

def resolve_url(request, lang_code, url_path):
    """ get a page """

    try:
        page, rest_url = PageTree.objects.get_page_from_url(url_path)
    except PageTree.DoesNotExist, err:
        return HttpResponseNotFound("<h1>Page not found</h1><h2>%s</h2>" % err)

    if page.type == PageTree.PLUGIN_TYPE:
        return HttpResponse("TODO: Plugin url: %r" % rest_url)

    try:
        lang = Language.objects.get(code=lang_code)
        content = PageContent.objects.get(lang=lang,page=page)
    except Language.DoesNotExist, PageContent.DoesNotExist:
        request.user.message_set.create(message="The page doesn't exist in the requested language.")
        # redirect to the existing language page
        new_url = reverse('PyLucid-existing_lang', kwargs={"url_path":url_path})
        return HttpResponseRedirect(new_url)

    return HttpResponse("lang: %r path: %r resolved_id: %r\n\n%r" % (lang_code, url_path, str(page.id),content.content))




#def get_page(request, page_id):
#    page = Page08.objects.get(id=page_id)
#    context = {
#        "page": page,
#    }
#    return render_to_response('pylucid/test.html', context)
