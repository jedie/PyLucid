# coding: utf-8

from django.conf import settings
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from pylucid_project.apps.pylucid.models import PageTree, PageContent
from pylucid_project.apps.pylucid_update.models import Page08

def menu(request):
    """ Display a menu with all update view links """
    context = {
        "title": "menu",
    }
    return render_to_response('pylucid_update/menu.html', context, context_instance=RequestContext(request))

def update08(request):
    """ Update PyLucid v0.8 model data to v0.9 models """
    old_pages = Page08.objects.all()
    for old_page in old_pages:
        print old_page
        
    raise NotImplementedError("TODO")
