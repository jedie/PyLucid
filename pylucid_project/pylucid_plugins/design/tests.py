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

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from dbtemplates.models import Template as DBTemplateModel

from django_tools.unittest_utils.unittest_base import BaseTestCase

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





class FixtureDataDesignTest(BaseTestCase, TestCase):
    fixtures = [
        # Special test users:
        os.path.join(settings.PYLUCID_BASE_PATH, "tests/fixtures/test_users.json"),
        DESIGN_UNITTEST_FIXTURES
    ]

    # normal: "* { color: {{ foreground }}; }\r\nbody { background: {{ background }}; }"
    # invert: "body { background: {{ foreground }}; }\r\n* { color: {{ background }}; }"
    # colorscheme1 (yellow):
    #    background: #222200;
    #    foreground: #aaaa00;
    # colorscheme2 (blue):
    #    background: #000040;
    #    foreground: #0000ff;

    YELLOW_STYLES = "* { color: #aaaa00; }\r\nbody { background: #222200; }"
    BLUE_STYLES = "* { color: #0000ff; }\r\nbody { background: #000040; }"
    INVERTED_BLUE_STYLES = "body { background: #0000ff; }\r\n* { color: #000040; }"
    INVERTED_YELLOW_STYLES = "body { background: #aaaa00; }\r\n* { color: #222200; }"

    def _pre_setup(self, *args, **kwargs):
        """
        Prepare
        """
        super(FixtureDataDesignTest, self)._pre_setup(*args, **kwargs)

        self.login("superuser")

        self.colorscheme1 = ColorScheme.objects.get(name="yellow")
        self.colorscheme2 = ColorScheme.objects.get(name="blue")

        #print EditableHtmlHeadFile.objects.all()
        self.headfile1 = EditableHtmlHeadFile.objects.get(filepath="test_styles.css")
        self.headfile2 = EditableHtmlHeadFile.objects.get(filepath="inverted_test_styles.css")

        self.url_edit_headfile = reverse("admin:pylucid_editablehtmlheadfile_change", args=(self.headfile1.id,))
        self.url_edit_colorscheme1 = reverse("admin:pylucid_colorscheme_change", args=(self.colorscheme1.pk,))
        self.url_edit_colorscheme2 = reverse("admin:pylucid_colorscheme_change", args=(self.colorscheme2.pk,))

        self.design1 = Design.objects.get(name="yellow")
        self.design2 = Design.objects.get(name="blue")
        self.design3 = Design.objects.get(name="inverted blue")
        self.design4 = Design.objects.get(name="inverted yellow")

        self.test_css_url1 = "/media/PyLucid/headfile_cache/ColorScheme_1/test_styles.css"
        self.test_css_url2 = "/media/PyLucid/headfile_cache/ColorScheme_2/test_styles.css"

    def setUp(self):
        self.clean_headfile_cache()
        self.assertEqual(Color.objects.all().filter(colorscheme=self.colorscheme1).count(), 2)
        self.assertEqual(Color.objects.all().filter(colorscheme=self.colorscheme2).count(), 2)

    def clean_headfile_cache(self):
        """ delete all cache files in cache directory """
        def delete_tree(path):
            if not os.path.isdir(path):
                return

            for dir_item in os.listdir(path):
                fullpath = os.path.join(path, dir_item)
                if os.path.isfile(fullpath):
                    os.remove(fullpath)
                elif os.path.isdir(fullpath):
                    delete_tree(fullpath)
                    os.rmdir(fullpath)

        pylucid_cache_path = os.path.join(
            settings.MEDIA_ROOT,
            settings.PYLUCID.PYLUCID_MEDIA_DIR,
            settings.PYLUCID.CACHE_DIR
        )
#        print "delete tree: %s " % pylucid_cache_path,
        delete_tree(pylucid_cache_path)
#        print "OK"

    def request_style(self, design):
        headfile = design.headfiles.all()[0]
        colorscheme = design.colorscheme
        url = headfile.get_absolute_url(colorscheme)
        self.assertTrue("/headfile_cache/" in url)
        response = self.client.get(url)
        return response

    def check_styles(self):
        response = self.request_style(self.design1)
        self.assertEqual(response.content, self.YELLOW_STYLES)
        response = self.request_style(self.design2)
        self.assertEqual(response.content, self.BLUE_STYLES)
        response = self.request_style(self.design3)
        self.assertEqual(response.content, self.INVERTED_BLUE_STYLES)
        response = self.request_style(self.design4)
        self.assertEqual(response.content, self.INVERTED_YELLOW_STYLES)

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

    def test_create_new_colors(self):
        new_content1 = self.headfile1.content + (
            "\r\n"
            "ul { color: #f00; }"
            "\r\n"
            "a { color: #ff0000; }"
        )
        new_content2 = self.headfile1.content + (
            "\r\n"
            "ul { color: {{ red }}; }"
            "\r\n"
            "a { color: {{ red }}; }"
        )


        response = self.client.post(self.url_edit_headfile,
            data={
                "filepath": self.headfile1.filepath,
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
        self.headfile1 = EditableHtmlHeadFile.objects.get(pk=self.headfile1.pk)
        self.assertEqual(self.headfile1.content, new_content2)

        # Check the rendered styles
        added_styles = (
            "\r\n"
            "ul { color: #ff0000; }"
            "\r\n"
            "a { color: #ff0000; }"
        )
        response = self.request_style(self.design1)
        self.assertEqual(response.content, self.YELLOW_STYLES + added_styles)
        response = self.request_style(self.design2)
        self.assertEqual(response.content, self.BLUE_STYLES + added_styles)

        # The inverted design, should not changed
        response = self.request_style(self.design3)
        self.assertEqual(response.content, self.INVERTED_BLUE_STYLES)
        response = self.request_style(self.design4)
        self.assertEqual(response.content, self.INVERTED_YELLOW_STYLES)

    def test_change_colors(self):
        response = self.client.post(
            self.url_edit_colorscheme1,
            data={'_continue': 'Save and continue editing',
                'color_set-0-colorscheme': '1',
                'color_set-0-id': '1',
                'color_set-0-name': 'background',
                'color_set-0-sites': '1',
                'color_set-0-value': '222200',
                'color_set-1-colorscheme': '1',
                'color_set-1-id': '2',
                'color_set-1-name': 'foreground',
                'color_set-1-sites': '1',
                'color_set-1-value': '0000ff',
                'color_set-INITIAL_FORMS': '2',
                'color_set-TOTAL_FORMS': '2',
                'color_set-__prefix__-colorscheme': '1',
                'color_set-__prefix__-sites': '1',
                'name': 'yellow',
                'sites': '1'}
        )
        self.assertRedirect(response, status_code=302,
            url="http://testserver" + self.url_edit_colorscheme1
        )
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
                'name="color_set-1-value" value="0000ff"',
            ),
            must_not_contain=("Traceback", "This field is required.")
        )
        # Changed yellow styles:
        response = self.request_style(self.design1)
        self.assertEqual(response.content, "* { color: #0000ff; }\r\nbody { background: #222200; }")
        response = self.request_style(self.design4)
        self.assertEqual(response.content, "body { background: #0000ff; }\r\n* { color: #222200; }")

        # Blue styles should not be changed:
        response = self.request_style(self.design2)
        self.assertEqual(response.content, self.BLUE_STYLES)
        response = self.request_style(self.design3)
        self.assertEqual(response.content, self.INVERTED_BLUE_STYLES)

    def test_rename_color(self):
        response = self.client.post(
            self.url_edit_colorscheme1,
            data={'_continue': 'Save and continue editing',
                'color_set-0-colorscheme': '1',
                'color_set-0-id': '1',
                'color_set-0-name': 'hintergrund',
                'color_set-0-sites': '1',
                'color_set-0-value': '222200',
                'color_set-1-colorscheme': '1',
                'color_set-1-id': '2',
                'color_set-1-name': 'vordergrund',
                'color_set-1-sites': '1',
                'color_set-1-value': 'aaaa00',
                'color_set-INITIAL_FORMS': '2',
                'color_set-TOTAL_FORMS': '2',
                'color_set-__prefix__-colorscheme': '1',
                'color_set-__prefix__-sites': '1',
                'name': 'yellow',
                'sites': '1'}
        )
        self.assertRedirect(response, status_code=302,
            url="http://testserver" + self.url_edit_colorscheme1
        )
        response = self.client.get(self.url_edit_colorscheme1)
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid - Change color scheme</title>',
                'colorpicker.css', 'colorpicker.js',
                'Change color scheme',

                # page message:                
                'Color &quot;background&quot; renamed to &quot;hintergrund&quot;:Headfiles &quot;test_styles.css&quot;, &quot;inverted_test_styles.css&quot; and colorschemes &quot;yellow&quot;, &quot;blue&quot; updated.',
                'Color &quot;foreground&quot; renamed to &quot;vordergrund&quot;:Headfiles &quot;test_styles.css&quot;, &quot;inverted_test_styles.css&quot; and colorschemes &quot;yellow&quot;, &quot;blue&quot; updated.',

                # colorscheme name:
                '<input name="name" value="yellow"',

                # colors:
                '<input name="color_set-0-name" value="hintergrund"',
                'name="color_set-0-value" value="222200"',
                '<input name="color_set-1-name" value="vordergrund"',
                'name="color_set-1-value" value="aaaa00"',
            ),
            must_not_contain=("Traceback", "This field is required.")
        )

        # Check sended styles, they must be the same
        self.check_styles()


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
#        failfast=True
    )
