#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
        - There exist only "PyLucid CMS" blog entry in english and german
        
    TODO:
        * Test clone colorscheme in admin
    
    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # run all unittest directly
    from django.core import management
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.core.urlresolvers import reverse
from django.conf import settings

from dbtemplates.models import Template as DBTemplateModel

from pylucid_project.apps.pylucid.models import PageMeta, Design, \
                                EditableHtmlHeadFile, ColorScheme, Color, PageTree
from pylucid_project.tests.test_tools import basetest

DESIGN_UNITTEST_FIXTURES = os.path.join(settings.PYLUCID_BASE_PATH, "pylucid_plugins", "design", "test_fixtures.json")


class CloneDesignTest(basetest.BaseUnittest):
    def _pre_setup(self, *args, **kwargs):
        super(CloneDesignTest, self)._pre_setup(*args, **kwargs)

        self.url = reverse("Design-clone")
        self.login("superuser")

    def test_request_form(self):
        response = self.client.get(self.url)
        self.assertResponse(response,
            must_contain=(
                "Clone a existing page design",
                '<input type="text" name="new_name"',
                '<select name="design"',
                "clone design",
            ),
            must_not_contain=("Traceback",)
        )

    def test_clone(self):
        new_name = "new_test_design"

        response = self.client.post(self.url, data={
            'design': Design.on_site.all()[0].pk,
            'new_name': new_name,
            'save': 'clone design',
            'sites': 1}
        )

        new_url = "http://testserver/pylucid_admin/plugins/design/clone/"
        self.assertRedirect(response, url=new_url, status_code=302)

        response = self.client.get(new_url)
        self.assertResponse(response,
            must_contain=(
                "Clone a existing page design",
                '<input type="text" name="new_name"',
                '<select name="design"',
                "clone design",
                "New design &#39;%s&#39; created." % new_name,
            ),
            must_not_contain=("Traceback",)
        )

        self.assertTrue(
            Design.objects.filter(name__exact=new_name).count() == 1
        )
        self.assertTrue(
            ColorScheme.objects.filter(name__exact=new_name).count() == 1
        )
        self.assertTrue(
            EditableHtmlHeadFile.objects.filter(filepath__startswith="%s/" % new_name).count() > 0
        )
        self.assertTrue(
            DBTemplateModel.objects.filter(name__exact="%s.html" % new_name).count() == 1
        )

#------------------------------------------------------------------------------






from django.test import TestCase
from django_tools.unittest_utils.unittest_base import BaseTestCase

class FixtureDataDesignTest(BaseTestCase, TestCase):
    fixtures = [
        # Special test users:
        os.path.join(settings.PYLUCID_BASE_PATH, "tests/fixtures/test_users.json"),
        DESIGN_UNITTEST_FIXTURES
    ]
    BLUE_STYLES = "* { color: #0000ff; }\r\nbody { background: #000040; }"
    YELLOW_STYLES = "* { color: #aaaa00; }\r\nbody { background: #222200; }"

    def _pre_setup(self, *args, **kwargs):
        """
        Prepare
        """
        super(FixtureDataDesignTest, self)._pre_setup(*args, **kwargs)

        self.login("superuser")

        self.colorscheme1 = ColorScheme.objects.get(name="yellow")
        self.colorscheme2 = ColorScheme.objects.get(name="blue")

        #print EditableHtmlHeadFile.objects.all()
        self.headfile = EditableHtmlHeadFile.objects.get(filepath="test_styles.css")

        self.url_edit_headfile = reverse("admin:pylucid_editablehtmlheadfile_change", args=(self.headfile.id,))
        self.url_edit_colorscheme1 = reverse("admin:pylucid_colorscheme_change", args=(self.colorscheme1.pk,))
        self.url_edit_colorscheme2 = reverse("admin:pylucid_colorscheme_change", args=(self.colorscheme2.pk,))

        self.design1 = Design.objects.get(name="yellow")
        self.design2 = Design.objects.get(name="blue")

        self.test_css_url1 = "/media/PyLucid/headfile_cache/ColorScheme_1/test_styles.css"
        self.test_css_url2 = "/media/PyLucid/headfile_cache/ColorScheme_2/test_styles.css"

    def setUp(self):
        self.clean_headfile_cache() # remove all cache files

    def clean_headfile_cache(self):
        for colorscheme in (self.colorscheme1, self.colorscheme2):
            self.headfile.delete_cachefile(colorscheme)

    def request_style(self, colorscheme):
        self.clean_headfile_cache()
        url = self.headfile.get_absolute_url(colorscheme)
        self.assertTrue("/headfile_cache/" in url)
        response = self.client.get(url)
        return response

    def test_fixture_loaded(self):
        self.assertEqual(Color.objects.all().filter(colorscheme=self.colorscheme1).count(), 2)
        self.assertEqual(Color.objects.all().filter(colorscheme=self.colorscheme2).count(), 2)

        response = self.request_style(self.colorscheme1)
        self.assertEqual(response.content, self.YELLOW_STYLES)
        response = self.request_style(self.colorscheme2)
        self.assertEqual(response.content, self.BLUE_STYLES)

    def test_yellow_page(self):
        response = self.client.get("/en/yellow/")
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid CMS - yellow</title>',
                '<link href="%s" rel="stylesheet" type="text/css" />' % self.test_css_url1,
                'yellow design test page content',
            ),
            must_not_contain=("Traceback",)
        )

    def test_blue_page(self):
        response = self.client.get("/en/blue/")
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid CMS - blue</title>',
                '<link href="%s" rel="stylesheet" type="text/css" />' % self.test_css_url2,
                'blue design test page content',
            ),
            must_not_contain=("Traceback",)
        )

    def test_design_admin_page(self):
        url = reverse("admin:pylucid_design_changelist")
        response = self.client.get(url)
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid - Select design to change</title>',

                # Color previews        
                '<span style="background-color:#222200;">',
                '<span style="background-color:#aaaa00;">',
                '<span style="background-color:#000040;">',
                '<span style="background-color:#0000ff;">',

                # edit template                
                '<a href="/admin/dbtemplates/template/1/"',
                'test_template.html</a>',

                # edit stylesheet
                '<a href="/admin/pylucid/editablehtmlheadfile/1/"',
                'test_styles.css',

                self.test_css_url1, self.test_css_url2,


            ),
            must_not_contain=("Traceback",)
        )

    def test_colorscheme_change(self):
        response = self.client.get(self.url_edit_colorscheme1)
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid - Change color scheme</title>',
                'colorpicker.css', 'colorpicker.js',
                'Change color scheme',

                # colorscheme name:
                '<input name="name" value="yellow"',

                # colors:
                '<input name="color_set-0-name" value="background"',
                'name="color_set-0-value" value="222200"',
                '<input name="color_set-1-name" value="foreground"',
                'name="color_set-1-value" value="aaaa00"',
            ),
            must_not_contain=("Traceback",)
        )

    #**************************************************************************

    def test_create_new_colors(self):
        new_content1 = self.headfile.content + (
            "\r\n"
            "ul { color: #f00; }"
            "\r\n"
            "a { color: #ff0000; }"
        )
        new_content2 = self.headfile.content + (
            "\r\n"
            "ul { color: {{ red }}; }"
            "\r\n"
            "a { color: {{ red }}; }"
        )


        response = self.client.post(self.url_edit_headfile,
            data={
                "filepath": self.headfile.filepath,
                "_continue": "",
                "render": 1,
                'sites': 1,
                "content": new_content1,
            }
        )
        self.assertRedirect(response, status_code=302,
            url="http://testserver" + self.url_edit_headfile
        )
        response = self.client.get(self.url_edit_headfile)
        self.assertResponse(response,
            must_contain=(
                "create colors: {&#39;red&#39;: u&#39;ff0000&#39;}"
                " in colorscheme: &quot;yellow&quot;, &quot;blue&quot;",

                new_content2,
                "was changed successfully. You may edit it again below.",
            ),
            must_not_contain=("Traceback",)
        )

        # Check if colors created
        self.assertEqual(Color.objects.all().filter(colorscheme=self.colorscheme1).count(), 3)
        self.assertEqual(Color.objects.all().filter(colorscheme=self.colorscheme2).count(), 3)

        # Check if headfile content really changed:
        self.headfile = EditableHtmlHeadFile.objects.get(pk=self.headfile.pk)
        self.assertEqual(self.headfile.content, new_content2)

        # Check the rendered styles
        added_styles = (
            "\r\n"
            "ul { color: #ff0000; }"
            "\r\n"
            "a { color: #ff0000; }"
        )
        response = self.request_style(self.colorscheme1)
        self.assertEqual(response.content, self.YELLOW_STYLES + added_styles)
        response = self.request_style(self.colorscheme2)
        self.assertEqual(response.content, self.BLUE_STYLES + added_styles)

    def test_change_colors(self):
        print "TODO!!!"





if __name__ == "__main__":
    # Run all unittest directly
#    management.call_command('test', "pylucid_plugins.design.tests.FixtureDataDesignTest",
##        verbosity=0,
##        verbosity=1,
#        verbosity=2,
#        failfast=True
#    )
    management.call_command('test', __file__,
        verbosity=2,
        failfast=True
    )
