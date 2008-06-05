 # -*- coding: utf-8 -*-

"""
    PyLucid page messages
    ~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from PyLucid.tools.content_processors import render_string_template
from PyLucid.middlewares.utils import is_html, replace_content

TAG = u"<!-- page_messages -->"

TEMPLATE = \
u"""<fieldset id="page_msg"><legend>page message</legend>
{% for message in page_msg %}\t{{ message }}<br />
{% endfor %}
</fieldset>"""

class PageMessagesMiddleware(object):
    def process_response(self, request, response):
        """
        insert all page messages into the html page.
        """
        if not is_html(response):
            # No HTML Page -> do nothing
            return response

        try:
            # get PyLucid.system.page_msg.PageMessages():
            page_msg = request.page_msg
        except AttributeError, e:
            message_string = "Error getting page_msg: %s" % e
        else:
            if len(page_msg) == 0:
                # There exists no page messages
                message_string = ""
            else:
                message_string = render_string_template(
                    TEMPLATE, context={"page_msg": page_msg}
                )

        response = replace_content(response, TAG, message_string)

        return response
