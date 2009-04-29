
from django.http import HttpResponse
from django.core.urlresolvers import reverse

def view_root(request):
    return HttpResponse("response: pluginpage_text.view_root !")
def view_a(request):
    return HttpResponse("response: pluginpage_text.view_a !")
def view_b(request):
    url = reverse("PluginTest-view_c")
    return HttpResponse("response: pluginpage_text.view_b: %s" % url)
def view_c(request):
    return HttpResponse("response: pluginpage_text.view_c !")