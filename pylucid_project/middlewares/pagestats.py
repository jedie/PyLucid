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
    
    Some SQL print stuff from: 
        http://www.djangosnippets.org/snippets/817/
    
    TODO:
    ~~~~~
    Put settings for debug_sql_queries() into settings.py:
        http://trac.pylucid.net/ticket/230

    :copyleft: 2007-2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import re
import time
import inspect
import collections

from django.conf import settings
from django.db import connection
from django.template.loader import render_to_string
from django.http import HttpResponse

# http://code.google.com/p/django-tools/
from django_tools.template.filters import human_duration

from pylucid_project.middlewares.utils import replace_content, cut_filename


# Save the start time of the current running python instance
start_overall = time.time()

TAG = u"<!-- script_duration -->"

# used if settings.DEBUG is off:
FMT = u"render time: %(total_time)s - overall: %(overall_time)s"
# used if settings.DEBUG is on:
FMT_DEBUG = FMT + u" - queries: %(query_count)d"

STACK_LIMIT = 5

FROM_REGEX = re.compile(
    r"(FROM|UPDATE|INTO)[\s`]+(.*?)[\s`]+",
    re.UNICODE | re.MULTILINE
)


class SqlLoggingList(list):
    """
    Append some infomation on every query in debug mode.
    TODO: Move this into django-tools as a seperate middleware!
    """
    def __init__(self, *args, **kwargs):
        self.type_count = collections.defaultdict(int)
        self.table_count = collections.defaultdict(int)
        super(SqlLoggingList, self).__init__(*args, **kwargs)

    def _pformat_sql(self, sql):
        sql = sql.replace('`', '')
        sql = sql.replace(' FROM ', '`FROM ')
        sql = sql.replace(' WHERE ', '`WHERE ')
        sql = sql.replace(' ORDER BY ', '`ORDER BY ')
        return sql.split('`')

    def append(self, query):
        sql = query["sql"].strip()
        sql_type = sql.split(" ", 1)[0]
        self.type_count[sql_type] += 1

        for table_info in FROM_REGEX.findall(sql):
            self.table_count[table_info[1]] += 1

        query["pformat"] = self._pformat_sql(sql)

        stack_list = inspect.stack()[1:]
        for no, stack_line in enumerate(stack_list):
            filename = stack_line[1]
            if "pylucid" in filename or "pylucid_project" in filename:
                break

        stack_list = stack_list[no:no + STACK_LIMIT] # limit the displayed stack info

        stack_info = []
        for stack_line in reversed(stack_list):
            stack_info.append({
                "filename": cut_filename(stack_line[1]),
                "lineno": stack_line[2],
                "func_name": stack_line[3],
                "code": stack_line[4]
            })

        query["stack_info"] = stack_info

        list.append(self, query)





class PageStatsMiddleware(object):
    def process_request(self, request):
        """
        save start time and database connections count.
        """
        self.start_time = time.time()
        if settings.DEBUG:
            # get number of db queries before we do anything
            self.old_queries = len(connection.queries)
            if settings.SQL_DEBUG:
                connection.queries = SqlLoggingList(connection.queries)

    def process_response(self, request, response):
        """
        calculate the statistic and replace it into the html page.
        """
        # Put only the statistic into HTML pages
        if (response.status_code != 200
            or not isinstance(response, HttpResponse)
            or "html" not in response["content-type"]):
            # No HTML Page -> do nothing
            return response

        try:
            start_time = self.start_time
        except AttributeError:
            # FIXME: process_request() was not called?!?
            return response

        context = {
            'total_time' : human_duration(time.time() - start_time),
            'overall_time' : human_duration(time.time() - start_overall),
        }

        if settings.DEBUG:
            # compute the db time for the queries just run, this information is
            # only available if the debug cursor used
            context["query_count"] = len(connection.queries) - self.old_queries
            stat_info = FMT_DEBUG % context
        else:
            # Used the template without queries
            stat_info = FMT % context

        # insert the page statistic
        response = replace_content(response, TAG, stat_info)

        if settings.DEBUG and settings.SQL_DEBUG:
            # Insert all SQL queries into html page
            context["queries"] = connection.queries
            context["type_count"] = dict(connection.queries.type_count)
            context["table_count"] = dict(connection.queries.table_count)
            sql_info = render_to_string("pylucid/sql_debug.html", context)
            response = replace_content(response, "</body>", sql_info)

        return response

