#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid page statistics
    ~~~~~~~~~~~~~~~~~~~~~~~

    A small page statistic middleware.
    -replace the >TAG< with some stats. But only in HTML pages.

    Based on http://code.djangoproject.com/wiki/PageStatsMiddleware

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from operator import add
from time import time
from django.db import connection
from django.core.exceptions import ImproperlyConfigured

start_overall = time()

TAG = "<!-- script_duration -->"

FMT = (
    'render time: %(total_time)s -'
    ' overall: %(overall_time)s -'
    ' Queries: %(queries)d'
)


def human_time(t):
    if t<1:
        return "%.1f ms" % (t * 100)
    elif t>60:
        return "%.1f min" % (t/60.0)
    else:
        return "%.1f sec" % t


class PageStatsMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        start_time = time()

        # get number of db queries before we do anything
        old_queries = len(connection.queries)

        try:
            # start the view
            response = view_func(request, *view_args, **view_kwargs)
        except AttributeError, e:
            if str(e)== "'WSGIRequest' object has no attribute 'user'":
                from django.conf import settings
                if not 'django.contrib.sessions.middleware.SessionMiddleware' \
                    in settings.MIDDLEWARE_CLASSES or not \
                    'django.contrib.auth.middleware.AuthenticationMiddleware' \
                    in settings.MIDDLEWARE_CLASSES:
                    msg = (
                        "You must include the session middleware and the"
                        " authentication middleware in your settings.py"
                        " after a syncdb. --- The original error message"
                        " was: %s"
                    ) % e
                    raise ImproperlyConfigured(msg)
            raise

        # Put only the statistic into HTML pages
        if response._headers.get('content-type', None) == "text/html":
            # No HTML Page -> do nothing
            return response

        # compute the db time for the queries just run
        queries = len(connection.queries) - old_queries

        total_time = human_time(time() - start_time)
        overall_time = human_time(time() - start_overall)

        # replace the comment if found
        stat_info = FMT % {
            'total_time' : total_time,
            'overall_time' : overall_time,
            'queries' : queries,
        }

        response.content = response.content.replace(TAG, stat_info)

        return response
