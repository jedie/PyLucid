#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
        - There exist only "PyLucid CMS" blog entry in english and german
    
    :copyleft: 2010-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.conf import settings
from django.contrib.comments.forms import CommentForm
from django.contrib.comments.models import Comment
from django.core import mail, signing
from django.test.client import Client

from django_tools.unittest_utils.BrowserDebug import debug_response

from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid.models import PageMeta
from pylucid_comments.views import _get_preferences

class PyLucidCommentsTestCase(basetest.BaseUnittest):
    def getValidData(self, obj, **kwargs):
        """ work-a-round for comment form security fields """
        f = CommentForm(obj)
        d = {
            'name'      : 'John Doe',
            'email'     : 'john.doe@example.tld',
            'url'       : '',
            'comment'   : 'This is my comment',
        }
        d.update(f.initial)
        d.update(kwargs)
        return d


class PyLucidCommentsPageMetaTestCase(PyLucidCommentsTestCase):
    """
    Base for all PageMeta tests.
    """
    def _pre_setup(self, *args, **kwargs):
        super(PyLucidCommentsTestCase, self)._pre_setup(*args, **kwargs)
        self.pagemeta = PageMeta.on_site.all()[0]
        self.absolute_url = self.pagemeta.get_absolute_url()
        self.get_form_url = self.absolute_url + "?pylucid_comments=get_form"
        self.submit_url = self.absolute_url + "?pylucid_comments=submit"

    def setUp(self):
        Comment.objects.all().delete()
        self._old_ADMINS = settings.ADMINS
        settings.ADMINS = (('John', 'john@example.com'), ('Mary', 'mary@example.com'))
        super(PyLucidCommentsTestCase, self).setUp()

    def tearDown(self):
        super(PyLucidCommentsTestCase, self).tearDown()
        settings.ADMINS = self._old_ADMINS

    def _get_form(self):
        data = self.getValidData(self.pagemeta)
        url = self.get_form_url
        url += "&content_type=%s" % data["content_type"]
        url += "&object_pk=%s" % data["object_pk"]
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        return response


class PyLucidCommentsPageMetaTest(PyLucidCommentsPageMetaTestCase):
    def test_get_form(self):
        """ get the comment form via AJAX """
        response = self._get_form()
        self.assertDOM(response,
            must_contain=(
                '<input id="id_content_type" name="content_type" type="hidden" value="pylucid.pagemeta" />',
                '<input id="id_object_pk" name="object_pk" type="hidden" value="%i" />' % self.pagemeta.pk,
                '<input checked="checked" id="id_notify" name="notify" type="checkbox" />'
            )
        )
        self.assertResponse(response,
            must_contain=(
                '<form action="JavaScript:void(0)" method="post" id="comment_form">',
            ),
            must_not_contain=(
                "Traceback", "Form errors", "field is required",
                "<body", "</html>"
            )
        )

    def test_submit_comment(self):
        settings.DEBUG = True # Display a comment error page
        self.failUnless(Comment.objects.count() == 0)
        self.failUnless(len(mail.outbox) == 0, len(mail.outbox))

        # submit a valid comments form
        data = self.getValidData(self.pagemeta, comment="from test_submit_comment()")
        response = self.client.post(self.submit_url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        # Check if comment created
        self.failUnless(Comment.objects.count() == 1)

        # Check if page should reload (JavaScript do this)
        self.failUnlessEqual(response.content, 'reload')

        # Check if ADMINS get's a email.
        #for email in mail.outbox:print email.message()

        self.assertEqual(len(mail.outbox), len(settings.ADMINS))

        email_text = mail.outbox[0].message()
        #print email_text
        self.failUnless("The comment is public." not in email_text)
        self.failUnless(data["name"] not in email_text)
        self.failUnless(data["comment"] not in email_text)
        self.failUnless("http://testserver%s" % self.absolute_url not in email_text)

        # Check if anonymous data saved in a cookie, for later usage
        self.failUnless("comments_data" in response.cookies)
        signed_comments_data = response.cookies["comments_data"].value
        comments_data = signing.loads(signed_comments_data)
        self.failUnlessEqual(
            comments_data,
            {u'url': u'', u'name': u'John Doe', u'email': u'john.doe@example.tld'}
        )

        # Check if anonymous data stored in cookie would be used:
        response = self._get_form()
        self.assertDOM(response,
            must_contain=(
                '<input id="id_name" maxlength="50" name="name" type="text" value="John Doe" />',
                '<input id="id_email" name="email" type="text" value="john.doe@example.tld" />',
            )
        )

    def test_submit_preview(self):
        settings.DEBUG = True # Display a comment error page
        self.failUnless(Comment.objects.count() == 0)
        url = self.absolute_url + "?pylucid_comments=submit"
        data = self.getValidData(self.pagemeta, preview="On", comment="comment from test_submit_preview()")
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertDOM(response,
            must_contain=(
                '<blockquote><p>comment from test_submit_preview()</p></blockquote>',
                '<input id="id_content_type" name="content_type" type="hidden" value="pylucid.pagemeta" />',
                '<input id="id_object_pk" name="object_pk" type="hidden" value="%i" />' % self.pagemeta.pk,
                '<input id="id_notify" name="notify" type="checkbox" />'
            )
        )
        self.assertResponse(response,
            must_contain=(
                'Preview your comment',
                '<form action="JavaScript:void(0)" method="post" id="comment_form">',
            ),
            must_not_contain=(
                "Traceback", "Form errors", "field is required",
                "<body", "</html>"
            )
        )

    def test_submit_no_comment(self):
        settings.DEBUG = True # Display a comment error page
        self.failUnless(Comment.objects.count() == 0)
        url = self.absolute_url + "?pylucid_comments=submit"
        data = self.getValidData(self.pagemeta, comment="", notify="on")
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.failUnless(Comment.objects.count() == 0)
        self.assertDOM(response,
            must_contain=(
                '<input id="id_content_type" name="content_type" type="hidden" value="pylucid.pagemeta" />',
                '<input id="id_object_pk" name="object_pk" type="hidden" value="%i" />' % self.pagemeta.pk,
                '<input checked="checked" id="id_notify" name="notify" type="checkbox" value="on" />'
            )
        )
        self.assertResponse(response,
            must_contain=(
                'Please correct the error below',
                'This field is required.',
                '<form action="JavaScript:void(0)" method="post" id="comment_form">',
            ),
            must_not_contain=("Traceback", "<body", "</html>")
        )

    def test_submit_spam(self):
        settings.DEBUG = True # Display a comment error page
        self.failUnless(Comment.objects.count() == 0)
        data = self.getValidData(self.pagemeta,
            comment="Penis enlargement pills: http://en.wikipedia.org/wiki/Penis_enlargement ;)"
        )
        response = self.client.post(self.submit_url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        # Check if page should reload (JavaScript do this)
        self.failUnlessEqual(response.content, 'reload')

        # Check if ADMINS get's a email.
        #for email in mail.outbox:print email.message()
        self.assertEqual(len(mail.outbox), len(settings.ADMINS))

        email_text = mail.outbox[0].message()
        #print email_text
        self.failUnless("The comment is public." not in email_text)
        self.failUnless(data["name"] not in email_text)
        self.failUnless(data["comment"] not in email_text)
        self.failUnless("http://testserver%s" % self.absolute_url not in email_text)

        # Check if comment created
        self.failUnless(Comment.objects.count() == 1)
        comment = Comment.objects.all()[0]
        self.failUnless(comment.is_public == False)

        # 'Reload' and check page message
        response = self.client.get(self.absolute_url)
        self.assertResponse(response,
            must_contain=(
                'Your comment waits for moderation.',
            ),
            must_not_contain=(
                "Traceback", "Form errors", "field is required",
                "Penis", "enlargement", "pills",
            )
        )

    def test_DOS_attack(self):
        settings.DEBUG = True # Display a comment error page
        self.failUnless(Comment.objects.count() == 0)
        url = self.absolute_url + "?pylucid_comments=submit"

        preferences = _get_preferences()
        ban_limit = preferences["ban_limit"]

        # Hold if all three events would been received. 
        tested_under_limit = False
        tested_limit_reached = False
        tested_banned = False

        for no in xrange(1, ban_limit + 2):
            # submit a valid comments form
            data = self.getValidData(self.pagemeta, comment="test_DOS_attack() comment no %i" % no)
            response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

            if no > ban_limit:
                # IP is on the ban list
                tested_banned = True
                self.assertStatusCode(response, 403) # get forbidden page
                comment_count = Comment.objects.count()
                self.failUnless(comment_count == ban_limit - 1)
            elif no == ban_limit:
                # The limit has been reached
                tested_limit_reached = True
                self.assertResponse(response, must_contain=('You are now banned.',))
                comment_count = Comment.objects.count()
                self.failUnless(comment_count == ban_limit - 1)
            else:
                # under ban limit: comment was saved, page should be reloaded
                tested_under_limit = True
                self.assertResponse(response,
                    must_contain=('reload',),
                    must_not_contain=(
                        "Traceback", "Form errors", "field is required",
                        "<!DOCTYPE", "<body", "</html>",
                    )
                )
                comment_count = Comment.objects.count()
                self.failUnless(comment_count == no)

        # Check if all three events have been received.
        self.failUnless(tested_limit_reached == True)
        self.failUnless(tested_under_limit == True)
        self.failUnless(tested_banned == True)


class PyLucidCommentsCsrfPageMetaTest(PyLucidCommentsPageMetaTestCase):
    """
    Test the Cross Site Request Forgery protection in comments.
    """
    def setUp(self):
        super(PyLucidCommentsPageMetaTestCase, self).setUp()
        settings.DEBUG = True
        self.client = Client(enforce_csrf_checks=True)

    def tearDown(self):
        super(PyLucidCommentsPageMetaTestCase, self).tearDown()
        settings.DEBUG = False

    def test_submit_form_without_token(self):
        # submit a valid comments form, but without csrf token 
        data = self.getValidData(self.pagemeta, comment="from test_submit_comment()")
        response = self.client.post(self.submit_url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertResponse(response, must_contain=("Forbidden", "CSRF cookie not set."))

    def test_submit_form_with_token(self):
        # get the current csrf token
        response = self._get_form()
        self.assertIn(settings.CSRF_COOKIE_NAME, response.cookies)
        csrf_token = response.cookies[settings.CSRF_COOKIE_NAME].value

        self.failUnless(Comment.objects.count() == 0)

        data = self.getValidData(self.pagemeta, comment="from test_submit_comment()")
        data["csrfmiddlewaretoken"] = csrf_token
        response = self.client.post(self.submit_url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        # Check if comment created
        self.failUnless(Comment.objects.count() == 1)

        # Check if page should reload (JavaScript do this)
        self.failUnlessEqual(response.content, 'reload')


if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management

    tests = __file__
#    tests = "pylucid_plugins.pylucid_comments.tests.PyLucidCommentsCsrfPageMetaTest"

    management.call_command('test', tests,
        verbosity=1,
#        verbosity=0,
#        failfast=True
    )
