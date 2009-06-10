# coding:utf-8

import os
import posixpath

import test_tools # before django imports!

from django.conf import settings

from django_tools.unittest import unittest_base

from pylucid_project.tests.test_tools import pylucid_test_data
from pylucid_project.tests.test_tools import basetest
from pylucid.models import EditableHtmlHeadFile


CSS_LINK = '<link href="%s" rel="stylesheet" type="text/css" />'


class DesignTest(basetest.BaseUnittest):
    def __init__(self, *args, **kwargs):
        super(DesignTest, self).__init__(*args, **kwargs)
        
        self.testcss1 = EditableHtmlHeadFile.objects.get(filepath=pylucid_test_data.TEST_CSS_FILEPATH1)
        self.testcss2 = EditableHtmlHeadFile.objects.get(filepath=pylucid_test_data.TEST_CSS_FILEPATH2)
        
        # fake django HttpRequest object, needed in UpdateInfoBaseModel save() method
        self.fake_request = pylucid_test_data.get_fake_request(usertype="superuser")

    def test_cached(self):
        """
        Test the stylesheet link, if the css file was cached into the filesystem.
        """
        # Create the cache file, if not exist
        for headfile in (self.testcss1, self.testcss2):
            cachepath = headfile.get_cachepath()
            if not os.path.isfile(cachepath):
                os.makedirs(os.path.dirname(cachepath)) # Cache dir doesn't exist?
                headfile.save(self.fake_request) # The save method should create the cache file
            # Check if file exist
            self.failUnless(os.path.isfile(cachepath), "Can't create cache file???")
            
        # Test urls in the page content
        response = self.client.get("/")
        self.assertResponse(response,
            must_contain=(
                '1-rootpage content', # PageContent
                '<title>1-rootpage title',
                
                # Design head file link with filesystem cache url:
                CSS_LINK % "/media/PyLucid/headfile_cache/unittest/test1.css",
                CSS_LINK % "/media/PyLucid/headfile_cache/unittest/test2.css",
            ),
            must_not_contain=(
                "Traceback",
            ),
        )

    def test_not_cached(self):
        """
        Test the stylesheet link, if the css file was *not* cached into the filesystem.
        """
        # remove style cache file, if exist
        for headfile in (self.testcss1, self.testcss2):
            cachepath = headfile.get_cachepath()
            if os.path.isfile(cachepath):
                os.remove(cachepath)
            self.failUnless(not os.path.isfile(cachepath), "Cache file exist???")
        
        # Check the urls in the page content
        response = self.client.get("/")
        self.assertResponse(response,
            must_contain=(
                '1-rootpage content', # PageContent
                '<title>1-rootpage title',
                
                # Design head file link with PyLucid own view url:
                CSS_LINK % "/headfile/unittest/test1.css",
                CSS_LINK % "/headfile/unittest/test2.css",
            ),
            must_not_contain=(
                "Traceback",
            ),
        )



if __name__ == "__main__":
    # Run this unitest directly
    unittest_base.direct_run(__file__)