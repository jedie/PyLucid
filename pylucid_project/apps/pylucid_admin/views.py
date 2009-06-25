# coding: utf-8

from django.conf import settings
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response


def menu(request):
    context = {
        "title": "PyLucid admin menu",
    }
    return render_to_response('pylucid_admin/menu.html', context,
        context_instance=RequestContext(request)
    )
