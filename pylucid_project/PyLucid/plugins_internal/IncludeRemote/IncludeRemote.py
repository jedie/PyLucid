# -*- coding: utf-8 -*-

"""
    PyLucid include remote plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Include remote content (received by urllib2.urlopen) into the CMS page
    content.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author$

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__= "$Rev: $"


import socket, urllib2, cgi, re, time

socket.setdefaulttimeout(5) # set a timeout

from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe

from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.tools.utils import escape as html_escape
from PyLucid.tools.utils import escape_django_tags

STRIP_CONTENT = (
    # stripe stylesheet links
    re.compile('(<link.*?rel.*?stylesheet.*?>)(?is)'),
    # strip javascript
    re.compile("(<script.*?</script>)(?is)")
)

META_CHARSET = re.compile('<meta.*?charset=(.*?)"')
BODY_RE = re.compile("<body.*?>(.*?)</body>(?is)")

class IncludeRemote(PyLucidBasePlugin):

    def lucidTag(self, url, title=None, preformat=None, escape=True):
        """
        docu about the method args, look into config file!
        """
        # get the remote content
        start_time = time.time()
        try:
            f = urllib2.urlopen(url)
            content = f.read()
            f.close()
        except Exception, err:
            if self.request.debug:
                self.page_msg.red("Include remote '%s' error: %s" % (url, err))
            return "[error getting '%s'.]" % title

        duration_time = time.time() - start_time

        #______________________________________________________________________
        # GET HEADER INFO

        content_type = None
        content_encodings = []

        # detect content type and encoding
        raw_content_type = f.headers.get("content-type")
        if raw_content_type:
            content_type, params = cgi.parse_header(raw_content_type)
            if "charset" in params:
                content_encodings.append(params["charset"])


        # Try to get content charset from html meta info
        try:
            charset = META_CHARSET.findall(content.lower())[0]
        except IndexError:
            pass
        except Exception, err:
            if self.request.debug:
                self.page_msg.red("Error get content charset:", err)
        else:
            content_encodings.append(charset)

        # decode into unicode
        content = self._decode_content(content, content_encodings)

        #______________________________________________________________________

        # try to cut out only the body content
        try:
            content = BODY_RE.findall(content)[0]
        except IndexError:
            pass
        except Exception, err:
            if self.request.debug:
                self.page_msg.red("Error strip body content:", err)

        #______________________________________________________________________
        # Strip content

        for regex in STRIP_CONTENT:
            try:
                content = regex.sub(u"",content)
            except Exception, err:
                if self.request.debug:
                    self.page_msg.red("Error strip content:", err)

        #______________________________________________________________________

        if escape:
            # Escape "&", "<", ">" and django template tags, e.g. "{" and "}"
            content = html_escape(content)
        else:
            # Escape only django template tags chars, e.g. "{" and "}"
            content = escape_django_tags(content)

        # turn django auto-escaping off
        content = mark_safe(content)

        # setup preformat
        if preformat==None and "html" in content_type:
            preformat = False
        else:
            preformat = True

        context = {
            "duration_time": duration_time,
            "url": url,
            "title": title,
            "content": content,
            "preformat": preformat,
        }
        self._render_template("IncludeRemote", context)#, debug=True)

    def _decode_content(self, content, content_encodings):
        """
        Try to decode content into unicode with the given encoding list.
        """
        if not content_encodings:
            # No charset found.
            return smart_unicode(content, errors='replace')

        errors = []
        for charset in content_encodings:
            try:
                content = content.decode(charset)
            except UnicodeDecodeError, err:
                errors.append(err)
            else:
                return content

        if self.request.debug:
            self.page_msg.red("Can't decode content:", errors)

        return smart_unicode(content, errors='replace')