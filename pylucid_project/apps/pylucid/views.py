

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response

#from pylucid_project.apps.pylucid.models import Page08


def root_page(request):
#    return HttpResponse("The root page!")
    context = {
        "page": "jojo",
    }
    return render_to_response('flatpages/default.html', context)

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
