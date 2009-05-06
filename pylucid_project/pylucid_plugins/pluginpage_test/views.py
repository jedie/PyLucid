
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response

def view_root(request):
    context = request.PYLUCID.context
    context["content"] = "pluginpage_text.view_root !"

    return render_to_response('pluginpage_test/test.html', context, 
        context_instance=RequestContext(request)
    )

def view_a(request):
    return HttpResponse("response: pluginpage_text.view_a !")
def view_b(request, url):
    url2 = reverse("PluginTest-view_c")
    return HttpResponse("response: %r pluginpage_text.view_b: %r" % (url2, url))
def view_c(request):
    return HttpResponse("response: pluginpage_text.view_c !")