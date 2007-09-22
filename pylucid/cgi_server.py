#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid CGI wrapper
    ~~~~~~~~~~~~~~~~~~~

    CGI wrapper for Django using the WSGI protocol.

    taken from http://code.djangoproject.com/ticket/2407
    original name: "cgi.py"

    Code copy/pasted from PEP-0333 and then tweaked to serve django.
    http://www.python.org/dev/peps/pep-0333/#the-server-gateway-side

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import os, sys
import django.core.handlers.wsgi

def runcgi():
    environ                      = dict(os.environ.items())
    environ['PATH_INFO']         = environ.get('PATH_INFO',"/")
    environ['wsgi.input']        = sys.stdin
    environ['wsgi.errors']       = sys.stderr
    environ['wsgi.version']      = (1,0)
    environ['wsgi.multithread']  = False
    environ['wsgi.multiprocess'] = True
    environ['wsgi.run_once']     = True

    application = django.core.handlers.wsgi.WSGIHandler()

    if environ.get('HTTPS','off') in ('on','1'):
        environ['wsgi.url_scheme'] = 'https'
    else:
        environ['wsgi.url_scheme'] = 'http'

    headers_set  = []
    headers_sent = []

    def send_content_type(response_headers):
        for no, header in enumerate(response_headers):
            if header[0].lower() == "content-type":
                sys.stdout.write('%s: %s\r\n' % header)
                del(response_headers[no])
                return response_headers

        sys.stdout.write('Content-Type: text/html\r\n')
        sys.stdout.write('Warning: Content Type not send!') # Bullshit?!?

    def write(data):
        if not headers_set:
            raise AssertionError("write() before start_response()")

        elif not headers_sent:
            # Before the first output, send the stored headers
            status, response_headers = headers_sent[:] = headers_set

            response_headers = send_content_type(response_headers) # Send Content-Type first

            if status == "500":
                sys.stdout.write("Content-type: text/html; charset=utf-8\r\n\r\nHARDCORE DEBUG:\n")
            sys.stdout.write('Status: %s\r\n' % status)
            for header in response_headers:
                sys.stdout.write('%s: %s\r\n' % header)
            sys.stdout.write('\r\n')

        sys.stdout.write(data)
        sys.stdout.flush()

    def start_response(status,response_headers,exc_info=None):
        if exc_info:
            try:
               if headers_sent:
                   # Re-raise original exception if headers sent
                   raise exc_info[0], exc_info[1], exc_info[2]
            finally:
               exc_info = None     # avoid dangling circular ref
        elif headers_set:
            raise AssertionError("Headers already set!")

        headers_set[:] = [status,response_headers]
        return write

    result = application(environ, start_response)
    try:
        for data in result:
            if data:    # don't send headers until body appears
                write(data)
        if not headers_sent:
            write('')   # send headers now if body was empty
    finally:
        if hasattr(result,'close'):
            result.close()
