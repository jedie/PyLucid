#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
        - There exist only "PyLucid CMS" blog entry in english and german
    
    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.conf import settings
from django.test.client import Client
from django.core.urlresolvers import reverse

from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid.models import PluginPage, PageContent, PageTree




class GalleryPluginTest(basetest.BaseUnittest):
    """
    inherited from BaseUnittest:
        - assertPyLucidPermissionDenied()
        - initial data fixtures with default test users
        - self.login()

    """
    def _pre_setup(self, *args, **kwargs):
        """ create some language related attributes """
        super(GalleryPluginTest, self)._pre_setup(*args, **kwargs)

        self.test_slug = "gallery_test"
        self.new_plugin_page_url = reverse("PageAdmin-new_plugin_page")
        self.gallerymodel_add_url = reverse("admin:gallery_gallerymodel_add")

        self.login("superuser")

    def test_create_page(self):
        """
        get the create page, with normal user witch has the add permission
        """
        response = self.client.post(self.new_plugin_page_url,
            data={'app_label': 'pylucid_project.pylucid_plugins.gallery',
            'design': 1,
            'position': 0,
            'slug': self.test_slug,
            'urls_filename': 'urls.py'
            }
        )
        # redirect from the save response to the new created plugin page
        page_url = "http://testserver/en/%s/" % self.test_slug
        self.assertRedirect(response, page_url, status_code=302)

        pagetree_id = PageTree.objects.get(slug=self.test_slug).id

        # redirect from plugin view to create the model data page
        response = self.client.get(page_url)
        self.assertRedirect(response,
            "http://testserver" + self.gallerymodel_add_url,
            status_code=302
        )

        base_path = "PyLucid"
        response = self.client.post(self.gallerymodel_add_url,
            data={
                'default_thumb_height': '100',
                'default_thumb_width': '100',
                'filename_suffix_filter': '_WEB,_web',
                'filename_whitelist': '*.jpg,*.jpeg,*.png',
                'pagetree': pagetree_id,
                'path': base_path,
                'template': 'gallery/default.html',
                'thumb_suffix_marker': '_thumb,_tmb'
            }
        )
        # After add the gallery model, it's going back to the gallery page
        self.assertRedirect(response, page_url, status_code=302)

        # Now we should see the gallery:
        response = self.client.get(page_url)
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid CMS - gallery_test</title>',
                'The gallery model &quot;GalleryModel for /gallery_test/&quot; was added successfully.',
                'Directory',
                '<li><a href="/en/gallery_test/superfish/">/superfish/</a> <small>(2 pictures)</small></li>',
                'Pictures',
                'Path',
                '''/<a href="/en/gallery_test/" title="goto 'index'">index</a>/''',
            ),
            must_not_contain=("Traceback", "Form errors", "field is required")
        )

        # go into a sub directory
        sub_dir = "markup_help"
        response = self.client.get(page_url + sub_dir + "/")
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid CMS - gallery_test</title>',
                'jquery.colorbox-min.js',
                '<img src="%s/markup_help/creole_cheat_sheet.png" alt="creole cheat sheet" width="100" height="100">' % (
                    settings.MEDIA_URL + base_path
                ),
                'Directory',
                'Pictures',
                'Path',
                '''<a href="/en/gallery_test/" title="goto 'index'">index</a>''',
                '''<a href="/en/gallery_test/%(dir)s/" title="goto '%(dir)s/'">markup_help</a>''' % {
                    "dir": sub_dir
                }
            ),
            must_not_contain=("Traceback", "Form errors", "field is required")
        )



if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management

    tests = __file__
#    tests = "pylucid_plugins.blog.tests.GalleryPluginArticleTest"

    management.call_command('test', tests ,
        verbosity=1,
#        verbosity=0,
#        failfast=True
    )
