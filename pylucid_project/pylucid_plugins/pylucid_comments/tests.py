#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
        - There exist only "PyLucid CMS" blog entry in english and german
    
    :copyleft: 2010 by the django-weave team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.conf import settings
from django.test.client import Client
from django.contrib.comments.models import Comment
from django.contrib.comments.forms import CommentForm

from django_tools.unittest_utils.BrowserDebug import debug_response

from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid.models import PageMeta

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
        

class PyLucidCommentsPageMetaTest(PyLucidCommentsTestCase):
    
    def _pre_setup(self, *args, **kwargs):
        super(PyLucidCommentsPageMetaTest, self)._pre_setup(*args, **kwargs)
        self.pagemeta = PageMeta.on_site.all()[0]
        self.absolute_url = self.pagemeta.get_absolute_url()
        
    def _get_form(self):
        url = self.absolute_url + "?pylucid_comments=get_form"
        data = self.getValidData(self.pagemeta)
        response = self.client.post(url,
            {
                "content_type": data["content_type"],
                "object_pk": data["object_pk"]
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        return response
    
    def test_get_form(self):
        """ get the comment form via AJAX """
        response = self._get_form()
        self.assertResponse(response,
            must_contain=(
                '<form action="JavaScript:void(0)" method="post" id="comment_form">',
                '<input type="hidden" name="content_type" value="pylucid.pagemeta"',
                '<input type="hidden" name="object_pk" value="%i"' % self.pagemeta.pk,
                '<input checked="checked" type="checkbox" name="notify" id="id_notify" />'
            ),
            must_not_contain=(
                "Traceback", "Form errors", "field is required",
                "<body", "</html>"
            )
        )
    
    def test_submit_comment(self):
        settings.DEBUG = True # Display a comment error page
        self.failUnless(Comment.objects.count() == 0)
        url = self.absolute_url + "?pylucid_comments=submit"
        
        # submit a valid comments form
        data = self.getValidData(self.pagemeta)
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        # Check if comment created
        self.failUnless(Comment.objects.count() == 1)
        
        # Check if page should reload (JavaScript do this)
        self.failUnlessEqual(response.content, 'reload')
        
        # Check if anonymous data saved in a cookie, for later usage
        self.failUnless("comments_data" in response.cookies)
        comments_data = response.cookies["comments_data"].value
        self.failUnless(comments_data.startswith("John Doe;john.doe@example.tld;"))
        
        # Check if anonymous data stored in cookie would be used:
        response = self._get_form()
        self.assertResponse(response,
            must_contain=(
                '<input id="id_name" type="text" name="name" value="John Doe" maxlength="50" />',
                '<input type="text" name="email" value="john.doe@example.tld" id="id_email" />',
            )
        )
        
    def test_submit_preview(self):
        settings.DEBUG = True # Display a comment error page
        self.failUnless(Comment.objects.count() == 0)
        url = self.absolute_url + "?pylucid_comments=submit"
        data = self.getValidData(self.pagemeta, preview="On")        
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertResponse(response,
            must_contain=(
                'Preview your comment',
                '<blockquote><p>This is my comment</p></blockquote>',
                '<form action="JavaScript:void(0)" method="post" id="comment_form">',
                '<input type="hidden" name="content_type" value="pylucid.pagemeta"',
                '<input type="hidden" name="object_pk" value="%i"' % self.pagemeta.pk,
                'type="checkbox" name="notify" id="id_notify" />',
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
        data = self.getValidData(self.pagemeta, comment="")
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.failUnless(Comment.objects.count() == 0)
        self.assertResponse(response,
            must_contain=(
                'Please correct the error below',
                'This field is required.',
                '<form action="JavaScript:void(0)" method="post" id="comment_form">',
                '<input type="hidden" name="content_type" value="pylucid.pagemeta"',
                '<input type="hidden" name="object_pk" value="%i"' % self.pagemeta.pk,
                'type="checkbox" name="notify" id="id_notify" />',
            ),
            must_not_contain=("Traceback", "<body", "</html>")
        )






if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management
#    management.call_command('test', "pylucid_plugins.blog.tests.BlogPluginArticleTest",
##        verbosity=0,
#        verbosity=1,
#        failfast=True
#    )
    management.call_command('test', __file__,
        verbosity=1,
#        verbosity=0,
        failfast=True
    )
