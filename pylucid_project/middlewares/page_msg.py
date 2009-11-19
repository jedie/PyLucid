 # coding: utf-8

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
import warnings
import traceback

from django.conf import settings
from django.utils.encoding import smart_str
from django.utils.safestring import SafeData, mark_safe
from django.template.loader import render_to_string

from pylucid_project.utils.escape import escape
from pylucid_project.middlewares.utils import replace_content, cut_filename

TAG = u"<!-- page_messages -->"

SESSION_KEY = "PAGE_MESSAGES"


STACK_LIMIT = 6


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

    def insert_traceback(self):
        """ Insert last traceback, if DEBUG==True """
        if not settings.DEBUG:
            return

        exc = traceback.format_exc()
        msg = mark_safe("<pre>%s</pre>" % exc)
        self.error(msg)

    #_________________________________________________________________________

    def showwarning(self, message, category, filename, lineno, file=None, line=None):
        """ for redirecting warnings """
        old_debug_mode = self.debug_mode
        self.debug_mode = False # no stack_info would be added
        self.warning(str(message))
        self.debug_mode = old_debug_mode

        # Add stack_info
        block_data = self.request.session[SESSION_KEY][-1]
        filename = u"..." + filename[-30:]
        block_data["stack_info"] = "(%s from %s - line %s)" % (category.__name__, filename, lineno)

        if file is not None:
            try:
                file.write(warnings.formatwarning(message, category, filename, lineno, line))
            except IOError:
                pass

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
                    lines[pos - 1] += " " + item

        block_data = {
            "msg_type": msg_type,
            "lines": lines,
        }

        if self.debug_mode == True:
            block_data["full_url"] = self.request.get_full_path()
            block_data["stack_info"] = self._get_stack_info()

        if SESSION_KEY not in self.request.session:
            # exemption: call page_msg directly after logout (session deleted)
            self.request.session[SESSION_KEY] = []

        self.request.session[SESSION_KEY].append(block_data)
        self.request.session.modified = True # FIXME: Don't really know why this is needed

    def _get_stack_info(self):
        """
        return stack_info: Where from the announcement comes?
        """
        self_basename = os.path.basename(__file__)
        if self_basename.endswith(".pyc"):
            # cut: ".pyc" -> ".py"
            self_basename = self_basename[:-1]

        stack_list = inspect.stack()
        # go forward in the stack, to outside of this file.
        for no, stack_line in enumerate(stack_list):
            filename = stack_line[1]
            if os.path.basename(filename) != self_basename:
                break

        stack_list = stack_list[no:no + STACK_LIMIT] # limit the displayed stack info

        stack_info = []
        for stack_line in reversed(stack_list):
            filename = cut_filename(stack_line[1])
            lineno = stack_line[2]
            func_name = stack_line[3]
            stack_info.append("%s %4s %s" % (filename, lineno, func_name))

        return "\\n\\n".join(stack_info)

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
            try:
                # e.g.: django ugettext_lazy string?
                return smart_str(unicode(txt), encoding=self._charset)
            except:
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




class PageMessagesMiddleware(object):
    def __init__(self):
        self.old_showwarning = warnings.showwarning
        self.tag = smart_str(TAG, encoding=settings.DEFAULT_CHARSET)

    def process_request(self, request):
        """ add page_msg object to request object """
        request.page_msg = PageMessages(request)

        # redirect warnings into page_msg
        warnings.showwarning = request.page_msg.showwarning

        #request.page_msg.add_test_lines()

    def process_response(self, request, response):
        """
        insert all page messages into the html page.
        """
        warnings.showwarning = self.old_showwarning

        if not hasattr(request, "session") or SESSION_KEY not in request.session:
            # There exist no session or page_msg -> do nothing
            return response

        if not "html" in response._headers["content-type"][1]:
            # No HTML Page -> do nothing
            return response

        content = response.content
        if self.tag not in content:
            # We can't replace the TAG with the page_msg if it's not in the content ;)
            # Do nothing and try it in the next request
            return response

        page_msg = request.page_msg
        if len(page_msg) == 0:
            # There exists no page messages
            message_string = ""
        else:
            request._cache_update_cache = False # Don't cache pages with page_msg

            # Get the messages and delete it from the session
            msg_list = page_msg.get_and_delete_messages()
            context = {
                "msg_list": msg_list,
                "stack_limit": STACK_LIMIT,
            }
            message_string = render_to_string("pylucid/page_msg.html", context)
            message_string = smart_str(message_string, encoding=settings.DEFAULT_CHARSET)

        response = replace_content(response, self.tag, message_string)

        return response
