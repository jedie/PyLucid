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
JS_LINK = '<script src="%s" type="text/javascript" language="javascript" /></script>'


class DesignTest(basetest.BaseUnittest):
    def __init__(self, *args, **kwargs):
        super(DesignTest, self).__init__(*args, **kwargs)

        self.test_css = EditableHtmlHeadFile.on_site.get(filepath=pylucid_test_data.TEST_CSS_FILEPATH)
        self.test_js = EditableHtmlHeadFile.on_site.get(filepath=pylucid_test_data.TEST_JS_FILEPATH)

    def _assert_headfiles(self, colorscheme, test_css_url, test_js_url):
        """ Test get_absolute_url() and head links in reponse content """
        self.failUnlessEqual(self.test_css.get_absolute_url(colorscheme), test_css_url)
        self.failUnlessEqual(self.test_js.get_absolute_url(colorscheme), test_js_url)

        # Test urls in the page content
        response = self.client.get("/")
        self.assertResponse(response,
            must_contain=(
                '1-rootpage content', # PageContent
                '<title>1-rootpage title',

                # Design head file links:
                CSS_LINK % test_css_url,
                JS_LINK % test_js_url,
            ),
            must_not_contain=(
                "Traceback",
            ),
        )

    def test_cached(self):
        """
        Test the stylesheet link, if the css file was cached into the filesystem.
        """
        colorscheme = None

        # Create the cache file, if not exist
        for headfile in (self.test_css, self.test_js):
            cachepath = headfile.get_cachepath(colorscheme)
            if not os.path.isfile(cachepath):
                cachedir = os.path.dirname(cachepath)
                if not os.path.isdir(cachedir):
                    os.makedirs()
                headfile.save() # The save method should create the cache file
            # Check if file exist
            self.failUnless(os.path.isfile(cachepath), "Cache file %r doesn't not exist?!?!" % cachepath)

        # Test get_absolute_url() and head links in reponse content
        self._assert_headfiles(colorscheme,
            "/media/PyLucid/headfile_cache/unittest/test.css",
            "/media/PyLucid/headfile_cache/unittest/test.js"
        )


    def test_not_cached(self):
        """
        Test the stylesheet link, if the css file was *not* cached into the filesystem.
        """
        colorscheme = None

        # remove style cache file, if exist
        for headfile in (self.test_css, self.test_js):
            cachepath = headfile.get_cachepath(colorscheme)
            if os.path.isfile(cachepath):
                os.remove(cachepath)
            self.failUnless(not os.path.isfile(cachepath), "Cache file exist???")

        # Test get_absolute_url() and head links in reponse content
        self._assert_headfiles(colorscheme,
            "/headfile/unittest/test.css",
            "/headfile/unittest/test.js"
        )

#    def test_colorscheme(self):





if __name__ == "__main__":
    # Run this unitest directly
    unittest_base.direct_run(__file__)
