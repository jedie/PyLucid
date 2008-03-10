#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test the global stylesheet handling.

    There exists two ways, how the global stylesheet can be response:
    -a fake file response with a _command url
    -save into a local cache file and include it with <link href=...>

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by the PyLucid team.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import os, re, posixpath

import tests

from django.conf import settings

from PyLucid.models import Page


# Regular Expression to get all stylesheets links from a content
# Must be updated, if the links aren't similarly structured.
LINK_HREF_RE = re.compile(
    '<link rel="stylesheet" type="text/css" href="(.+?)" />'
)


# The content of the test stylesheet:
TEST_STYLE_CONTENT = "X test stylesheet! X"



class TestStylesheet(tests.TestCase):

    def setUp(self):
        """
        Create a clean page table.
        Create the test pages with a test template and stylesheet.
        """
        Page.objects.all().delete() # Delete all existins pages

        self.template = tests.create_template("{% lucidTag page_style %}")
        self.style = tests.create_stylesheet(
            name = "TestStyle", content = TEST_STYLE_CONTENT,
        )

        # Create the test pages defined in content_test_utils.py
        # assign the test template and stylesheet to all pages
        tests.create_pages(
            tests.TEST_PAGES,
            template=self.template,
            style = self.style,
        )

    #--------------------------------------------------------------------------

    def _exctract_stylelinks(self, content):
        """
        Returns all stylesheet links.
        """
        return LINK_HREF_RE.findall(content)

    def _get_stylelink(self):
        """ Local implementation of models.Style.get_absolute_url() """
        return posixpath.join(
            "", settings.MEDIA_URL, settings.PYLUCID_MEDIA_DIR,
            self.style.name + ".css",
        )

    def _get_stylepath(self):
        """ Local implementation of models.Style.get_filepath() """
        return posixpath.join(
            "", settings.MEDIA_ROOT, settings.PYLUCID_MEDIA_DIR,
            self.style.name + ".css",
        )

    def _get_content_link(self):
        """ Return the stylesheet link contains in the root cms page. """
        response = self.client.get("/")
        content = response.content
        links = self._exctract_stylelinks(content)
        assert len(links) == 1
        return links[0]

    #--------------------------------------------------------------------------

    def test_model_link(self):
        """
        Test if the local implementation of a style link works on the same way
        as models.Style.get_absolute_url()
        """
        must_link = self._get_stylelink()
        is_link = self.style.get_absolute_url()
        assert is_link == must_link

    def test_model_path(self):
        """
        Test if the local implementation of a style path works on the same way
        as models.Style.get_filepath()
        """
        must_path = self._get_stylepath()
        is_path = self.style.get_filepath()
        assert is_path == must_path

    def test_style_conent(self):
        """
        Test the content of the style instance.
        """
        assert self.style.content == TEST_STYLE_CONTENT

    def test_CSS_cache_file(self):
        """
        Test the local CSS cache file.

        We create in self.setUp() a new stylesheet. The model method
        models.Style.save() stored the CSS content in a local cache file into
        the media path. Check if the file exists and if the content the same.
        """
        must_path = self._get_stylepath()
        is_path = self.style.get_filepath()
        assert is_path == must_path
        assert os.path.isfile(is_path) == True

        file_content = file(is_path, "r").read()
        assert file_content == TEST_STYLE_CONTENT

    #--------------------------------------------------------------------------

    def test_content_link(self):
        """
        Check the link to the stylesheets, if the CSS cache file exists.
            e.g.: /media/PyLucid/TestStyle.css

        -request a page content
        -exctract the contained style link
        -check if it's a link to the cache file.
        """
        must_link = self._get_stylelink()
        is_link = self._get_content_link()
        assert is_link == must_link

    def test_command_link(self):
        """
        Check the link to the stylesheet, without a CSS cache file.
            e.g.: /_command/1/page_style/sendStyle/TestStyle.css

        -delete the local CSS cache file
        -request a page content
        -exctract the contained style link
        -check if the style link work
        """
        # Delete the CSS file
        filepath = self._get_stylepath()
        os.remove(filepath)

        # Request a cms page and get the style link from the content
        link = self._get_content_link()
        assert settings.COMMAND_URL_PREFIX in link

        # request the stylesheet via _command link
        response = self.client.get(link)
        assert response.content == TEST_STYLE_CONTENT



if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])