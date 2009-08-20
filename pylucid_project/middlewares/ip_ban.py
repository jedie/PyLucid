# coding: utf-8

import time
import datetime

from django import http
from django.conf import settings
from django.core.exceptions import PermissionDenied

from pylucid.preference_forms import SystemPreferencesForm


forbidden_response = http.HttpResponseForbidden(
"""<html><head><title>403 Forbidden</title></head><body>
<h1>403 Forbidden</h1><p>This resource is unavailable at this time from this computer.</p>
</body></html>""")


sys_pref_form = SystemPreferencesForm()
sys_pref = sys_pref_form.get_preferences()
ban_release_time = sys_pref["ban_release_time"]
ban_release_timedelta = datetime.timedelta(minutes=ban_release_time)

class IPBanMiddleware(object):
    def __init__(self):
        self.cleanup_ip_ban = settings.PYLUCID.CLEANUP_IP_BAN
        self.next_check = 0 # Check the first call

    def process_request(self, request):
        from pylucid.models import BanEntry # FIXME: against import loops.

        remote_addr = request.META["REMOTE_ADDR"]
        should_ban = BanEntry.objects.filter(ip_address=remote_addr).count()
        if should_ban > 0:
#            raise PermissionDenied("This resource is unavailable at this time from this computer.")
#            raise http.Http404("This resource is unavailable at this time from this computer.")
            return forbidden_response

        if time.time() > self.next_check:
            # Delete all old BanEntry
            self.next_check = time.time() + self.cleanup_ip_ban # Save for next time
            BanEntry.objects.cleanup(request, ban_release_timedelta)


