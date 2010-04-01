#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    TODO: Test colorscheme stuff
    
    :copyleft: 2010 by the django-weave team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from pylucid_project.tests.test_tools import basetest
from pylucid_project.tests.test_tools.scrapping import HTMLscrapper
from pylucid_project.apps.pylucid.models import EditableHtmlHeadFile, ColorScheme



class DesignTestCase(basetest.BaseUnittest):
    STYLES = ['initial_site_style/main.css', 'pygments.css'] # used on the index page

    def _pre_setup(self, *args, **kwargs):
        super(DesignTestCase, self)._pre_setup(*args, **kwargs)

        self.colorscheme = ColorScheme.objects.get(id=1) # used in index page

        self.headfiles = []
        for style_path in self.STYLES:
            headfile = EditableHtmlHeadFile.on_site.get(filepath=style_path)
            self.headfiles.append(headfile)

    def get_headlinks(self, response):
        data = HTMLscrapper().grab(response.content, tags=("link",), attrs=("href",))
        return [url for url in data["href"] if "headfile" in url]

    def assertHeadfiles(self, urls):
        for url in urls:
            response = self.client.get(url)
            self.assertStatusCode(response, 200)
            self.failUnlessEqual(response["content-type"], "text/css")

    def check_headfile(self, headfile, colorscheme):
        url = headfile.get_absolute_url(colorscheme)
        self.assertHeadfiles([url])


class DesignTest(DesignTestCase):

    def test_index_styles(self):
        """ grab style links from index page and test if they can be requested """
        response = self.client.get("/")
        urls = self.get_headlinks(response)
        self.failUnless(len(urls) == 2)
        self.assertHeadfiles(urls)

    def test_cache(self):
        """ Test cached and non cache requests """
        # Create the cache file, if not exist
        for headfile in self.headfiles:
            cachepath = headfile.get_cachepath(self.colorscheme)
            if os.path.isfile(cachepath):
                # remove cache file
                os.remove(cachepath)
                self.failIf(os.path.isfile(cachepath), "Can't delete %r ?!?!" % cachepath)

            # Check if headfile.get_absolute_url can be requested
            self.check_headfile(headfile, self.colorscheme)

            headfile.save() # The save method should create the cache file

            # Check if file exist
            self.failUnless(os.path.isfile(cachepath), "Cache file %r doesn't not exist?!?!" % cachepath)

            # Check if headfile.get_absolute_url can be requested
            self.check_headfile(headfile, self.colorscheme)



if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management
    management.call_command('test', __file__, verbosity=1)
