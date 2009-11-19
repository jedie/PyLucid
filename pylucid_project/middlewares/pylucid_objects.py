# coding: utf-8

import traceback

from pylucid.system import pylucid_objects
from pylucid.models import LogEntry

class PyLucidMiddleware(object):
    def process_request(self, request):
        """ Add PyLucid objects to the request object """
        request.PYLUCID = pylucid_objects.PyLucidRequestObjects(request)

    def process_exception(self, request, exception):
        LogEntry.objects.log_action(
            app_label="pylucid", action="PyLucidMiddleware.process_exception()", message=str(exception),
            long_message=traceback.format_exc()
        )
