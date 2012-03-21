# coding: utf-8

"""
    PyLucid middleware
    ~~~~~~~~~~~~~~~~~~
    
    Create request.PYLUCID and log process_exception()
    
    TODO: Move IP-Ban + Log stuff into a separate app
    
    :copyleft: 2009-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import traceback

from django.conf import settings
from django.contrib.redirects.models import Redirect
from django.http import Http404
from django.utils.encoding import smart_str
from django.core.exceptions import SuspiciousOperation

from pylucid_project.apps.pylucid.models import LogEntry
from pylucid_project.apps.pylucid.system import pylucid_objects

class SuspiciousOperation404(SuspiciousOperation):
    """
    A SuspiciousOperation that will return a normal 404 back to the client.
    But this error would be logged and the IP would be ban if the client
    raised to much exceptions.
    The 404 would be returned in PyLucidMiddleware.process_exception()
    """
    # TODO: Move logging, ip ban and this into a seperate app
    status_code = 404


class PyLucidMiddleware(object):
    def process_request(self, request):
        """ Add PyLucid objects to the request object """
        request.PYLUCID = pylucid_objects.PyLucidRequestObjects(request)

    def process_exception(self, request, exception):
        # Get the system preferences
        sys_pref = request.PYLUCID.preferences
        sys_pref_form = request.PYLUCID.preferences_form

        if isinstance(exception, Http404):
            # Handle 404 page not found errors
            log404_verbosity = sys_pref.get("log404_verbosity", sys_pref_form.LOG404_NOREDIRECT)

            if log404_verbosity == sys_pref_form.LOG404_NOTHING:
                # Don't log 'Page not found' errors.
                return

            # Check if there exist a django.contrib.redirects entry for this url
            path = request.get_full_path()
            try:
                r = Redirect.objects.get(site__id__exact=settings.SITE_ID, old_path=path)
            except Redirect.DoesNotExist:
                LogEntry.objects.log_action(
                    app_label="pylucid", action="PyLucidMiddleware.process_exception()",
                    message="Redirect for %r doesn't exist." % path
                )
                return
            else:
                # Redirect entry exist
                if log404_verbosity == sys_pref_form.LOG404_NOREDIRECT:
                    # Log only 'Page not found' if no redirect for the url exists.
                    return

                LogEntry.objects.log_action(
                    app_label="pylucid", action="PyLucidMiddleware.process_exception()",
                    message="Redirect for %r exist." % path
                )
                return

        # cut exception message text to LogEntry.message max_length, to get no "Data truncated..." warning
        message = smart_str(exception, errors='replace')[:255]

        LogEntry.objects.log_action(
            app_label="pylucid", action="PyLucidMiddleware.process_exception()", message=message,
            long_message=traceback.format_exc()
        )

        ban_time = sys_pref["ban_time"] # Time period for count exceptions log messages from the same IP.
        ban_count = sys_pref["ban_count"] # Numbers of exceptions from one IP within 'ban_time' after the IP would be banned. 

        # Count the last requests for this app_label
        queryset = LogEntry.objects.last_remote_addr_actions(request, ban_time)
        queryset = queryset.filter(app_label="pylucid")
        queryset = queryset.filter(action="PyLucidMiddleware.process_exception()")
        last_actions = queryset.count()

        if last_actions >= ban_count:
            from pylucid_project.apps.pylucid.models import BanEntry
            BanEntry.objects.add(request) # raised 404 after adding the client IP!

        if isinstance(exception, SuspiciousOperation404):
            # raise a normal 404 after SuspiciousOperation was logged.
            raise Http404("SuspiciousOperation.")
