#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
   PyLucid.tests.utils.FakeRequest
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   Helper functions for creating fake request objects.

   :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
   :license: GNU GPL v3, see LICENSE.txt for more details.
"""

#______________________________________________________________________________
# Fake PyLucid Environment

class FakePageMsg(object):
    """
    faked PyLucid.system.page_msg.PageMessages()
    """
    def __call__(self, *msg):
        self.write(*msg)

    def write(self, *msg):
        for line in msg:
            print line

    def DEBUG(self, *msg):
        self.write(*msg)

    def black(self, *msg):
        self.write(*msg)

    def green(self, *msg):
        self.write(*msg)

    def red(self, *msg):
        self.write(*msg)


class FakeUser(object):
    def is_anonymous(self):
        return True

class FakeRequest(object):
    __fake_http_host = "unitest_HTTP_HOST_fake"
    user = FakeUser()
    META = {"HTTP_HOST": __fake_http_host,}
    debug = True
    page_msg = FakePageMsg()
    def get_host(self):
        """
        django's request.get_host()
        http://www.djangoproject.com/documentation/request_response/#id1
          Returns the originating host of the request using information from
          the HTTP_X_FORWARDED_HOST and HTTP_HOST headers (in that order). If
          they don’t provide a value, the method uses a combination of
          SERVER_NAME and SERVER_PORT as detailed in PEP 333.
        Example: "127.0.0.1:8000"
        """
        return self.__fake_http_host

class FakePage(object):
    id = 1

def get_fake_context(page_object=None):
    if not page_object:
        from PyLucid.models import Page
        try:
            page_object = Page.objects.get(id=1)
        except Exception:
            # Does only works, if the PyLucid dump inserted to the database
            page_object = FakePage()

    fake_context = {
        "request": FakeRequest(),
#        "page_msg": ,
        "PAGE": page_object,
        "CSS_ID_list": [],

    }
    from PyLucid.system.URLs import URLs
    fake_context["URLs"] = URLs(fake_context)

    return fake_context
