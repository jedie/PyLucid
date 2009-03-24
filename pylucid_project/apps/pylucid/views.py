

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response

from pylucid_project.apps.pylucid.models import Page08


def get_page(request, page_id):
    page = Page08.objects.get(id=page_id)
    context = {
        "page": page,
    }
    return render_to_response('pylucid/test.html', context)