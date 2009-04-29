
from django.http import HttpResponse
from django.core.urlresolvers import reverse

def view_root(request):
    return HttpResponse("response: pluginpage_text.view_root !")
def view_a(request):
    return HttpResponse("response: pluginpage_text.view_a !")
def view_b(request, url):
    url2 = reverse("PluginTest-view_c")
    return HttpResponse("response: %r pluginpage_text.view_b: %r" % (url2, url))
def view_c(request):
    return HttpResponse("response: pluginpage_text.view_c !")