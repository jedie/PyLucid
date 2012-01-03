# coding: utf-8

"""
    IPBanMiddleware
    ~~~~~~~~~~~~~~~
    
    Block banned IP addresses and delete old pylucid.models.BanEntry items:
    
    TODO: Move IP-Ban + Log stuff into a separate app
    
    :copyleft: 2009-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import time
import datetime

from django import http
from django.conf import settings


forbidden_response = http.HttpResponseForbidden(
"""<html><head><title>403 Forbidden</title></head><body>
<h1>403 Forbidden</h1><p>This resource is unavailable at this time from this computer.</p>
</body></html>""")


class IPBanMiddleware(object):
    def __init__(self):
        self.cleanup_ip_ban = settings.PYLUCID.CLEANUP_IP_BAN
        self.ban_release_timedelta = datetime.timedelta(minutes=settings.PYLUCID.BAN_RELEASE_TIME)
        self.next_check = 0 # Check the first call

    def process_request(self, request):
        from pylucid_project.apps.pylucid.models import BanEntry # FIXME: against import loops.

        remote_addr = request.META["REMOTE_ADDR"]
        should_ban = BanEntry.objects.filter(ip_address=remote_addr).count()
        if should_ban > 0:
#            raise PermissionDenied("This resource is unavailable at this time from this computer.")
#            raise http.Http404("This resource is unavailable at this time from this computer.")
            return forbidden_response

        if time.time() > self.next_check:
            # Delete all old BanEntry
            self.next_check = time.time() + self.cleanup_ip_ban # Save for next time
            BanEntry.objects.cleanup(request, self.ban_release_timedelta)


