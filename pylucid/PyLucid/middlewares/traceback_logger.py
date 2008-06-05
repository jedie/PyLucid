# -*- coding: utf-8 -*-

"""
    PyLucid traceback logger
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Tries to catch all tracebacks in the process_view view_func and write
    it into the log file.

    Should not be used in a productive environment!
    
    ToDo:
        handle process_exception()

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from operator import add
from time import time

from django.http import HttpResponse

from PyLucid.template_addons.filters import human_duration


LOGFILE = "PyLucid_fcgi.log"

start_overall = time()

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    filename=LOGFILE,
    filemode='a'
)
log = logging.debug
log("TLM - TracebackLogMiddleware started")


class TracebackLogMiddleware(object):
#    def process_request(self, request):
#        log("TLM - process_request()")

    def process_view(self, request, view_func, view_args, view_kwargs):
        log("TLM - process_view()")
        start_time = time()

        try:
            # start the view
            response = view_func(request, *view_args, **view_kwargs)
        except Exception, e:
            msg = "Error: %s" % e
            log(msg)
            response = HttpResponse()
            response.write(msg)

        total_time = human_duration(time() - start_time)
        overall_time = human_duration(time() - start_overall)

        time_info = "total time: %s - overall_time: %s" % (
            total_time, overall_time
        )
        log(time_info)

        response.content += time_info

        return response

#    def process_response(self, request, response):
#        log("TLM - process_response()")
##        log(response.content)
#        return response

#    def process_exception(self, request, exception):
#        log("TLM - process_exception()")
        