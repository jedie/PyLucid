

from django.conf import settings
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

#from pylucid_project.apps.pylucid.models import Page08

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
    return HttpResponse("root page for lang: %r" % lang_code)

def resolve_url(request, lang_code, url_path):
    """ get a page """
    return HttpResponse("lang: %r path: %r" % (lang_code, url_path))



#def get_page(request, page_id):
#    page = Page08.objects.get(id=page_id)
#    context = {
#        "page": page,
#    }
#    return render_to_response('pylucid/test.html', context)
