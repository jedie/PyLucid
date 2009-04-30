 # -*- coding: utf-8 -*-

"""
    PyLucid page messages
    ~~~~~~~~~~~~~~~~~~~~~

    A small Wrapper aound djangos user messages system.

    enhanced features:
      - easy callable to print a messages
      - simple color output: self.page_msg.green()
      - use pprint for dicts and lists
      - special debug mode:
          Inserts informationen, where from the message has come.

    Can also used in Plugin for storing internal messages.

    Links
    ~~~~~
    http://www.pylucid.org/_goto/134/plugin-output/
    http://www.djangoproject.com/documentation/authentication/#messages

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys
import pprint
import inspect

from django.conf import settings
from django.utils.encoding import smart_str
from django.template import Context, Template
from django.utils.safestring import mark_safe, SafeData

from pylucid_project.utils.escape import escape

TAG = "<!-- page_messages -->"

SESSION_KEY = "PAGE_MESSAGES"

TEMPLATE = \
"""<fieldset id="page_msg"><legend>page message</legend>
{% for message in msg_list %}\t{{ message }}<br />
{% endfor %}
</fieldset>"""



class PageMessages(object):
    """
    The page message container.
    """
    def __init__(self, request, html=True):
        self.request = request
        self.html = html # Should we generate colored html output?

        try:
            session = request.session
        except AttributeError, err:
            raise AttributeError("Can't the sessin object."
                " PageMessagesMiddleware must be added *after* SessionMiddleware!"
                " original error was: %s" % err)

        if SESSION_KEY not in session:
            # Add a page_msg list into session
            session[SESSION_KEY] = []

        self.debug_mode = settings.DEBUG
        self._charset = settings.DEFAULT_CHARSET
    
    def get_and_delete_messages(self):
        """ delete messages from session and return them """#
        self.append_django_messages()
        msg = self.request.session[SESSION_KEY]
        # remove "old" page_msg from session
        del(self.request.session[SESSION_KEY])
        return msg
    
    def append_django_messages(self):
        """ Append messages from django """
        django_msg = self.request.user.get_and_delete_messages()
        for msg in django_msg:
            self.black(msg)
        
    #_________________________________________________________________________

    def write(self, *msg):
        self.append_color_data("blue", *msg)

    def __call__(self, *msg):
        """ Alte Methode um Daten "auszugeben", Text ist dann schwarz """
        self.append_color_data("blue", *msg)

    def DEBUG(self, *msg):
        self.append_color_data("gray", *msg)

    def black(self, *msg):
        self.append_color_data("black", *msg)

    def green(self, *msg):
        self.append_color_data("green", *msg)

    def red(self, *msg):
        self.append_color_data("red", *msg)

    #_________________________________________________________________________

    def append_color_data(self, color, *msg):
        self.append_django_messages()
        if self.html:
            msg = '<span style="color:%s;">%s</span>' % (
                color, self.prepare(*msg)
            )
        else:
            msg = self.prepare(*msg)

        msg = mark_safe(msg) # turn djngo auto-escaping off
        self.request.session[SESSION_KEY].append(msg)

    def _get_fileinfo(self):
        """
        Append the fileinfo: Where from the announcement comes?
        """
        try:
            self_basename = os.path.basename(__file__)
            if self_basename.endswith(".pyc"):
                # cut: ".pyc" -> ".py"
                self_basename = self_basename[:-1]
#                result.append("1%s1" % self_basename)

            for stack_frame in inspect.stack():
                # go forward in the stack, to outside of this file.
                filename = stack_frame[1]
                lineno = stack_frame[2]
#                    result.append("2%s2" % os.path.basename(filename))
                if os.path.basename(filename) != self_basename:
#                        result.append("\n")
                    break

            filename = "...%s" % filename[-25:]
            fileinfo = "%-25s line %3s: " % (filename, lineno)
        except Exception, e:
            fileinfo = "(inspect Error: %s)" % e

        return fileinfo

    def prepare(self, *msg):
        """
        -if debug_mode is on: insert a info from where the message sended.
        -for dict, list use pprint ;)
        """
        if self.debug_mode == True:
            result = [self._get_fileinfo()]
        else:
            result = []

        for item in msg:
            if isinstance(item, dict) or isinstance(item, list):
                item = pprint.pformat(item)
                item = item.split("\n")
                for line in item:
                    line = self.encode_and_prepare(line)
                    if self.html:
                        result.append("%s<br />\n" % line)
                    else:
                        result.append("%s\n" % line)
            else:
                item = self.encode_and_prepare(item)
                result.append(item)
                result.append(" ")

        result = "".join(result).strip()
        return result

    def encode_and_prepare(self, txt):
        """
        Pass "safe" strings, all other would be escaped.
        """
        if isinstance(txt, SafeData):
            return txt

        if not isinstance(txt, basestring):
            txt = repr(txt)
        elif isinstance(txt, unicode):
            txt = smart_str(txt, encoding=self._charset)

        return escape(txt)

    #________________________________________________________________

    def __repr__(self):
        return "page messages: %s" % repr(self.request.session[SESSION_KEY])

    def __str__(self):
        return "pages messages: %s" % ", ".join(self.request.session[SESSION_KEY])

    def __unicode__(self):
        return u"page messages: %s" % u", ".join(self.request.session[SESSION_KEY])

    def __len__(self):
        return len(self.request.session[SESSION_KEY])


def render_string_template(template, context):
    """ render the given template string """
    t = Template(template)
    c = Context(context)
    return t.render(c)




class PageMessagesMiddleware(object):
    def process_request(self, request):
        """ add page_msg object to request object """
        request.page_msg = PageMessages(request)
        
    def process_response(self, request, response):
        """
        insert all page messages into the html page.
        """
        def save_session(request):
            if request.session[SESSION_KEY]:
                # FIXME: Don't really know why this is needed
                request.session.save()
        
        if not "html" in response._headers["content-type"][1]:
            # No HTML Page -> do nothing
            save_session(request)
            return response

        content = response.content
        if not TAG in content:
            # We can't replace the TAG with the page_msg if it's not in the content ;)
            # Do nothing and try it in the next request
            save_session(request)
            return response

        page_msg = request.page_msg
        if len(page_msg) == 0:
            # There exists no page messages
            message_string = ""
        else:
            # Get the messages and delete it from the session
            msg_list = page_msg.get_and_delete_messages()
            message_string = render_string_template(
                TEMPLATE, context={"msg_list": msg_list}
            )
            message_string = smart_str(message_string)

        new_content = content.replace(TAG, message_string)
        response.content = new_content
        
        return response
