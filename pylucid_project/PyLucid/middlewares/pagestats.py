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

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from time import time

from django.db import connection

from PyLucid.template_addons.filters import human_duration
from PyLucid.middlewares.utils import is_html, replace_content

# Save the start time of the current running pyhon instance
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
        if not is_html(response):
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

        # insert the page statistic
        response = replace_content(response, TAG, stat_info)

        #response = self.debug_sql_queries(response)

        return response

    def debug_sql_queries(self, response):
        """
        Insert all SQL queries.
        ONLY for developers!
        """
        show_only = ("PyLucid_plugin", "PyLucid_preference2")
        sql_info = "<h2>Debug SQL queries:</h2>"
        if show_only:
            sql_info += "Show only: %s" % ", ".join(show_only)
        sql_info += "<pre>"
        for q in connection.queries:
            sql = q['sql']
            if show_only:
                table_name = sql.split(' FROM "')[1].split('"', 1)[0]
                if table_name not in show_only:
                    continue

            time = float(q['time'])

            sql = sql.replace(' FROM "', '\nFROM "')
            sql = sql.replace(' WHERE "', '\nWHERE "')
            sql_info += "\n%s\n%s\n" % (time, sql)
        sql_info += "</pre></body>"

        response = replace_content(response, "</body>", sql_info)

        return response