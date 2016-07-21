
from django.conf import settings
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect

from multisite.models import Alias


def auto_create_alias(request):
    """
    Create a multisite.models.Alias entry for the current host.
    Use the default SITE_ID.

    Use by add this into settings:

    MULTISITE_FALLBACK="pylucid.multisite_views.auto_create_alias"

    see also:
    https://github.com/ecometrica/django-multisite/issues/33
    """
    host = request.get_host().lower()
    site_id = settings.SITE_ID.get_default()
    site = Site.objects.get(pk=site_id)

    # print("Create Alias for %r to SITE_ID %s" % (host, site.pk))
    Alias.objects.create(
        domain=host,
        site=site,
        redirect_to_canonical=False,
    )
    return HttpResponseRedirect(request.get_full_path())
