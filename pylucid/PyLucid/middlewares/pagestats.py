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

from time import time

from django.db import connection

from PyLucid.template_addons.filters import human_duration

start_overall = time()

TAG = u"<!-- script_duration -->"

FMT = (
    u'render time: %(total_time)s -'
    ' overall: %(overall_time)s -'
    ' queries: %(queries)d'
)

class PageStatsMiddleware(object):
    def process_request(self, request):
        """
        save start time and database connections count.
        """
        self.start_time = time()
        # get number of db queries before we do anything
        self.old_queries = len(connection.queries)

    def process_response(self, request, response):
        """
        calculate the statistic and replace it into the html page.
        """
        # Put only the statistic into HTML pages
        if not "html" in response._headers["content-type"][1]:
            # No HTML Page -> do nothing
            return response

        # compute the db time for the queries just run
        # FIXME: In my shared webhosting environment the queries is always = 0
        queries = len(connection.queries) - self.old_queries

        total_time = human_duration(time() - self.start_time)
        overall_time = human_duration(time() - start_overall)

        # replace the comment if found
        stat_info = FMT % {
            'total_time' : total_time,
            'overall_time' : overall_time,
            'queries' : queries,
        }

        content = response.content
        if not isinstance(content, unicode):
            # FIXME: In my shared webhosting environment is response.content a
            # string and not unicode. Why?
            from django.utils.encoding import force_unicode
            try:
                content = force_unicode(content)
            except:
                return response

        # insert the page statistic
        new_content = content.replace(TAG, stat_info)
        response.content = new_content

        return response
