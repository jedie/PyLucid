#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid Plugin - IncludeRemote

Include remote content (received by urllib2.urlopen) into the CMS page content.

Last commit info:
----------------------------------
$LastChangedDate: $
$Rev: $
$Author: JensDiemer $

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

__version__= "$Rev: $"


import socket, urllib2, re, time

socket.setdefaulttimeout(5) # set a timeout

from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe

from PyLucid.system.BasePlugin import PyLucidBasePlugin


class IncludeRemote(PyLucidBasePlugin):

    def lucidTag(self, url, title=None, escape=True):

        # get the remote content
        start_time = time.time()
        try:
            f = urllib2.urlopen(url)
            content = f.read()
            f.close()
        except Exception, e:
            return (
                "<p>IncludeRemote error! Can't get '%s'<br />"
                " error:'%s'</p>"
            ) % (url, e)
        duration_time = time.time() - start_time


        # cutout stylesheets
        try:
            content = re.sub(
                '(<link.*?rel.*?stylesheet.*?>)(?is)',"",content
            )
        except:
            pass


        # cutout JavaScripts
        try:
            content = re.sub(
                '(<script.*?</script>)(?is)',"",content
            )
        except:
            pass


        # decode into unicode
        try:
            charset = re.findall(
                '<meta.*?content-type.*?charset=(.*?)"', content.lower()
            )[0]
            content = content.decode(charset)
        except:
            content = smart_unicode(content, errors='replace')


        # try to cut out only the body content
        try:
            content = re.findall("<body.*?>(.*?)</body>(?is)", content)[0]
        except:
            pass


        if not escape:
            # turn djngo auto-escaping off
            content = mark_safe(content)


        context = {
            "duration_time": duration_time,
            "url": url,
            "title": title,
            "content": content,
        }
        self._render_template("IncludeRemote", context)#, debug=True)
