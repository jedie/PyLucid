 # coding: utf-8

"""
    PyLucid page statistics
    ~~~~~~~~~~~~~~~~~~~~~~~

    A small page statistic middleware.
    -replace the >TAG< with some stats. But only in HTML pages.

    Based on http://code.djangoproject.com/wiki/PageStatsMiddleware
    
    database queries
    ~~~~~~~~~~~~~~~~
    We display only the the database queries count if debug is on. Otherwise
    the database cursor doesn't count the sql statements and we always get 0 ;)
    
    TODO:
    ~~~~~
    Put settings for debug_sql_queries() into settings.py:
        http://trac.pylucid.net/ticket/230

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import time

from django.conf import settings
from django.db import connection

# http://code.google.com/p/django-tools/
from django_tools.template.filters import human_duration

from pylucid_project.middlewares.utils import replace_content

# Save the start time of the current running python instance
start_overall = time.time()

TAG = u"<!-- script_duration -->"

# used if settings.DEBUG is off:
FMT = u"render time: %(total_time)s - overall: %(overall_time)s"
# used if settings.DEBUG is on:
FMT_DEBUG = FMT + u" - queries: %(queries)d"


class PageStatsMiddleware(object):
    def process_request(self, request):
        """
        save start time and database connections count.
        """
        self.start_time = time.time()
        if settings.DEBUG:
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

        context = {
            'total_time' : human_duration(time.time() - self.start_time),
            'overall_time' : human_duration(time.time() - start_overall),
        }

        if settings.DEBUG:
            # compute the db time for the queries just run, this information is
            # only available if the debug cursor used
            context["queries"] = len(connection.queries) - self.old_queries
            stat_info = FMT_DEBUG % context
        else:
            # Used the template without queries
            stat_info = FMT % context

        # insert the page statistic
        response = replace_content(response, TAG, stat_info)

#        response = self.debug_sql_queries(response)

        return response

    def debug_sql_queries(self, response):
        """
        Insert all SQL queries.
        ONLY for developers!
        """
        sql_info = "<h2>Debug SQL queries:</h2>"
        sql_info += "<pre>"
        for q in connection.queries:
            sql = q['sql']
            time = float(q['time'])
            sql = sql.replace(' FROM "', '\nFROM "')
            sql = sql.replace(' WHERE "', '\nWHERE "')
            sql_info += "\n%s\n%s\n" % (time, sql)
        sql_info += "</pre></body>"

        response = replace_content(response, "</body>", sql_info)

        return response
