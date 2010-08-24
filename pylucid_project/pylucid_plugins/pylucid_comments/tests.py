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
    
    def test_get_form(self):
        """ get the comment form via AJAX """
        url = self.absolute_url + "?pylucid_comments=get_form"
        data = self.getValidData(self.pagemeta)
        response = self.client.post(url,
            {
                "content_type": data["content_type"],
                "object_pk": data["object_pk"]
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertResponse(response,
            must_contain=(
                '<form action="JavaScript:void(0)" method="post" id="comment_form">',
                '<input type="hidden" name="content_type" value="pylucid.pagemeta"',
                '<input type="hidden" name="object_pk" value="%i"' % self.pagemeta.pk,
                '<label for="id_notify">Notify</label>',
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
        data = self.getValidData(self.pagemeta)
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.failUnless(Comment.objects.count() == 1)
        self.failUnlessEqual(response.content, '<script type="text/javascript">location.reload();</script>')
        
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
                '<label for="id_notify">Notify</label>',
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
                '<label for="id_notify">Notify</label>',
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
