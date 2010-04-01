# coding:utf-8

from django import http
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from redirect.models import RedirectModel


def setup_view(request):
    """
    called to setup a page entry
    TODO: This must be implemented in PyLucid, see also:
    http://pylucid.org/phpBB2/viewtopic.php?p=1551&highlight=setup+view#1551 (de)
    """
    pass


def redirect(request, rest_url=""):
    pagetree = request.PYLUCID.pagetree
    #lang_entry = request.PYLUCID.current_language

    try:
        redirect_info = RedirectModel.objects.get(pagetree=pagetree)#, language=lang_entry)
    except RedirectModel.DoesNotExist, err:
        # TODO: Don't redirect to admin panel -> Display a own create view!
        request.page_msg(
             _("Redirect entry for page: %s doesn't exist, please create.") % pagetree.get_absolute_url()
        )
        return HttpResponseRedirect(reverse("admin:redirect_redirectmodel_add"))

    destination_url = redirect_info.destination_url

    #print "rest_url: %r" % rest_url
    rest_url = rest_url.lstrip("/")
    if rest_url: # Handel the additional url part
        if not redirect_info.full_url:
            # raise 404, because we should not match on the full url.
            msg = ""
            if settings.DEBUG or request.user.is_staff:
                msg += " URL has additional parts %r, but 'full_url' is not allowed." % rest_url
            raise http.Http404(msg)
        destination_url += rest_url

    if request.GET and redirect_info.append_query_string:
        # Add GET query string
        # We don't use request.GET.urlencode() here, because it can change the key positions
        full_path = request.get_full_path()
        get_string = full_path.split("?", 1)[1]
        destination_url += "?" + get_string

    response_data = redirect_info.get_response_data()

    # get HttpResponsePermanentRedirect or HttpResponseRedirect class
    response_class = response_data["class"]
    response = response_class(destination_url)

    if settings.DEBUG or request.user.is_staff:
        msg = "You redirected from %r to %r (%s)" % (
            request.path, destination_url, response_data["title"]
        )
        if redirect_info.debug:
            return "Debug: %s" % msg
        else:
            request.page_msg.info(msg)

    return response

def redirect_index(request):
    return redirect(request)
