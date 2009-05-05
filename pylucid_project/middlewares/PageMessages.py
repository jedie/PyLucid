 # -*- coding: utf-8 -*-

"""
    PyLucid page messages
    ~~~~~~~~~~~~~~~~~~~~~

    A small Wrapper aound djangos user messages system.

    enhanced features:
      - easy callable to print a messages
      - simple color output: self.page_msg.successful()
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
from django.utils.safestring import SafeData, mark_safe

from pylucid_project.utils.escape import escape

TAG = "<!-- page_messages -->"

SESSION_KEY = "PAGE_MESSAGES"

MAX_FILEPATH_LEN = 60

TEMPLATE = \
"""<fieldset id="page_msg"><legend>page message</legend>
{% for message in msg_list %}
<p class="{{ message.msg_type }}"{% if message.fileinfo %} title="{{ message.fileinfo }}"{% endif %}>
{% for line in message.lines %}{{ line }}{% if not forloop.last %}<br />{% endif %}
{% endfor %}</p>
{% endfor %}
</fieldset>"""



class PageMessages(object):
    """
    The page message container.
    """
    def __init__(self, request):
        self.request = request

        self.debug_mode = settings.DEBUG
        self._charset = settings.DEFAULT_CHARSET

        try:
            session = request.session
        except AttributeError, err:
            raise AttributeError("Can't the sessin object."
                " PageMessagesMiddleware must be added *after* SessionMiddleware!"
                " original error was: %s" % err)

        if SESSION_KEY not in session:
            # Add a page_msg list into session
            session[SESSION_KEY] = []
        elif session[SESSION_KEY] != []:
            # There exist old messages from previous requests -> add a seperator after them. 
            self.info(mark_safe("<hr />"))
    
    def get_and_delete_messages(self):
        """ delete messages from session and return them """
        django_msg = self.request.user.get_and_delete_messages()
        for msg in django_msg:
            # Append messages from django
            self.info(msg)
            
        msg = self.request.session[SESSION_KEY]
        # remove "old" page_msg from session
        del(self.request.session[SESSION_KEY])
        return msg
        
    #_________________________________________________________________________

    def write(self, *msg):
        self.append_message("info", *msg)

    def __call__(self, *msg):
        self.append_message("info", *msg)

    def successful(self, *msg):
        self.append_message("successful", *msg)

    def info(self, *msg):
        self.append_message("info", *msg)

    def warning(self, *msg):
        self.append_message("warning", *msg)

    def error(self, *msg):
        self.append_message("error", *msg)

    def critical(self, *msg):
        self.append_message("critical", *msg)

    #_________________________________________________________________________

    def append_message(self, msg_type, *msg):       
        """
        Add a message with type info.
        -if debug_mode is on: insert a info from where the message sended.
        -for dict, list use pprint ;)
        """
        lines = []
        for raw_item in msg:
            if isinstance(raw_item, dict) or isinstance(raw_item, list):
                item = pprint.pformat(raw_item)
                raw_lines = item.split("\n")
                for raw_line in raw_lines:
                    lines.append(self.encode_and_prepare(raw_line))
                lines.append("")
            else:
                item = self.encode_and_prepare(raw_item)
                pos = len(lines)
                if pos == 0:
                    lines.append(item)
                else:
                    lines[pos-1] += " " + item
        
        block_data = {
            "msg_type": msg_type,
            "lines": lines,
        }
        
        if self.debug_mode == True:
            block_data["fileinfo"] = self._get_fileinfo()

        self.request.session[SESSION_KEY].append(block_data)
        self.request.session.modified = True # FIXME: Don't really know why this is needed

    def _get_fileinfo(self):
        """
        return fileinfo: Where from the announcement comes?
        """
        try:
            self_basename = os.path.basename(__file__)
            if self_basename.endswith(".pyc"):
                # cut: ".pyc" -> ".py"
                self_basename = self_basename[:-1]

            for stack_frame in inspect.stack():
                # go forward in the stack, to outside of this file.
                filename = stack_frame[1]
                lineno = stack_frame[2]
                if os.path.basename(filename) != self_basename:
                    break

            if len(filename)>=MAX_FILEPATH_LEN:
                filename = "...%s" % filename[-MAX_FILEPATH_LEN:]
            fileinfo = "%s line %s" % (filename, lineno)
        except Exception, e:
            fileinfo = "(inspect Error: %s)" % e

        return fileinfo


    def encode_and_prepare(self, txt):
        """ prepare the given text """
        if isinstance(txt, SafeData):
            # pass string witch marked with django.utils.safestring.mark_safe
            return txt            
        elif isinstance(txt, unicode):
            # encode unicode strings
            return smart_str(txt, encoding=self._charset)
        elif isinstance(txt, str):
            # pass normal strings
            return txt
        else:
            # return the printable representation of an object
            return repr(txt)
        

    #________________________________________________________________
    
    def add_test_lines(self):
        """ Add many test lines """
        self.append_message("successful", "test successful line")
        self.append_message("info", "test info line")
        self.append_message("warning", "test warning line")
        self.append_message("error", "test error line")
        self.append_message("critical", "test critical line")
        self.append_message("info", "Here comes:", ["a", "messages", "list"], "and text after the list.")
        self.append_message("info", "Here is:", {"a":"dict"}, "and text after a dict.")
        self.append_message("warning", "<html characters should be escaped.>")
        self.append_message("warning", mark_safe("You can use <strong>mark_safe</strong> to use html code."))
        

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
        #request.page_msg.add_test_lines()
        
    def process_response(self, request, response):
        """
        insert all page messages into the html page.
        """        
        if not "html" in response._headers["content-type"][1]:
            # No HTML Page -> do nothing
            return response

        content = response.content
        if not TAG in content:
            # We can't replace the TAG with the page_msg if it's not in the content ;)
            # Do nothing and try it in the next request
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
