# -*- coding: utf-8 -*-

"""
    The PyLucid page message system
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os, sys, pprint, inspect

from django.utils.safestring import mark_safe, SafeData
from django.utils.encoding import force_unicode

from django.conf import settings

from PyLucid.tools.utils import escape

#_____________________________________________________________________________

class PageMessages(object):
    """
    The page message container.
    """
    def __init__(self, request, use_django_msg=True, html=True):
        self.html = html # Should we generate colored html output?

        self.messages = []
        if use_django_msg:
            try:
                self.messages = request.user.get_and_delete_messages()
            except AttributeError:
                # In the _install section we have no user
                pass

        self.debug_mode = getattr(request, "debug", False)

        self._charset = settings.DEFAULT_CHARSET

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
        if self.html:
            msg = '<span style="color:%s;">%s</span>' % (
                color, self.prepare(*msg)
            )
        else:
            msg = self.prepare(*msg)

        #~ self.request.user.message_set.create(message=msg)
        msg = mark_safe(msg) # turn djngo auto-escaping off
        self.messages.append(msg)

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

        if not isinstance(txt, unicode):
            txt = force_unicode(txt)

        return escape(txt)

    #________________________________________________________________

    def __repr__(self):
        return "page messages: %s" % repr(self.messages)

    def __str__(self):
        return "pages messages: %s" % ", ".join(self.messages)

    def __unicode__(self):
        return u"page messages: %s" % u", ".join(self.messages)

    #________________________________________________________________
    # Some methods for the django template engine:

    def __iter__(self):
        """
        used in: {% for message in page_msg %}
        """
        for message in self.messages:
            yield message

    def __len__(self):
        """
        used in: {% if page_msg %}
        """
        return len(self.messages)





