#!/usr/bin/env python
# coding: utf-8


"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
        - There exist only "PyLucid CMS" blog entry in english and german
        
    TODO:
        * Rewrite tests if we use django-compressor
        * Test clone colorscheme in admin
    
    :copyleft: 2010-2011 by the PyLucid team, see AUTHORS for more details.
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

from pylucid_project.apps.pylucid.models import Design, EditableHtmlHeadFile, ColorScheme, Color
from pylucid_project.tests.test_tools import basetest


DESIGN_UNITTEST_FIXTURES = os.path.join(settings.PYLUCID_BASE_PATH, "pylucid_plugins", "design", "test_fixtures.json")


class SwitchDesignTest(basetest.BaseUnittest):
    def _pre_setup(self, *args, **kwargs):
        super(SwitchDesignTest, self)._pre_setup(*args, **kwargs)

        self.url = reverse("Design-switch")
        self.login("superuser")

    def test_request_form(self):
        response = self.client.get(self.url)
        self.assertResponse(response,
            must_contain=(
                "Switch a PyLucid page design",
                '<option value="0" selected="selected">&lt;automatic&gt;</option>',
                self.url,
            ),
            must_not_contain=("Traceback", "XXX INVALID TEMPLATE STRING")
        )

    def test_switch(self):
        # request root page before switch design
        response = self.client.get("/en/welcome/")
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid CMS - Welcome to your PyLucid CMS =;-)</title>'
                'initial_site_style/main.css" rel="stylesheet"'
                '<div id="the_menu">'
            ),
            must_not_contain=("Traceback", "XXX INVALID TEMPLATE STRING")
        )

        # switch design
        response = self.client.post(self.url, data={"design":4}, follow=True)
        self.assertResponse(response,
            must_contain=(
                "Switch a PyLucid page design",
                'Save design ID 4',
                'current page design is switched to: <strong>Page design &#39;elementary&#39;',
                '<option value="4" selected="selected">elementary</option>',
            ),
            must_not_contain=("Traceback", "XXX INVALID TEMPLATE STRING")
        )

        # request root page after design switch
        response = self.client.get("/en/welcome/")
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid CMS - Welcome to your PyLucid CMS =;-)</title>'
                'initial_site_style/elementary.css" rel="stylesheet"'
            ),
            must_not_contain=('<div id="the_menu">', "Traceback", "XXX INVALID TEMPLATE STRING")
        )

        # Delete design and test request
        Design.objects.get(id=4).delete()

        # Should switch back to main design and give a page messages
        response = self.client.get("/en/welcome/")
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid CMS - Welcome to your PyLucid CMS =;-)</title>',
                'initial_site_style/main.css" rel="stylesheet"',
                'Can&#39;t switch to design with ID 4: Design matching query does not exist.',
            ),
            must_not_contain=("Traceback", "XXX INVALID TEMPLATE STRING")
        )


class CloneDesignTest(basetest.BaseUnittest, TestCase):
    def _pre_setup(self, *args, **kwargs):
        super(CloneDesignTest, self)._pre_setup(*args, **kwargs)

        self.url = reverse("Design-clone")
        self.login("superuser")

    def test_request_form(self):
        response = self.client.get(self.url)
        self.assertDOM(response,
            must_contain=(
                '<input id="id_new_name" name="new_name" type="text" />',
            )
        )
        self.assertResponse(response,
            must_contain=(
                "Clone a existing page design",
                '<select', 'id="id_design"', 'name="design"',
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
        self.assertDOM(response,
            must_contain=(
                '<input id="id_new_name" name="new_name" type="text" />',
            )
        )
        self.assertResponse(response,
            must_contain=(
                "Clone a existing page design",
                '<select', 'id="id_design"', 'name="design"',
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

        self.test_css_url1 = "/static/PyLucid_cache/ColorScheme_1/test_styles.css"
        self.test_css_url2 = "/static/PyLucid_cache/ColorScheme_2/test_styles.css"

    def setUp(self):
        removed_items = EditableHtmlHeadFile.objects.clean_headfile_cache()
        #print removed_items
        self.assertEqual(Color.objects.all().filter(colorscheme=self.colorscheme1).count(), 2)
        self.assertEqual(Color.objects.all().filter(colorscheme=self.colorscheme2).count(), 2)

        self._old_debug = settings.DEBUG
        settings.DEBUG = True # Needed to serve static files

    def tearDown(self):
        settings.DEBUG = self._old_debug

    def request_style(self, design):
        headfile = design.headfiles.all()[0]
        colorscheme = design.colorscheme
        url = headfile.get_absolute_url(colorscheme)
        self.assertTrue("/PyLucid_cache/" in url)
        response = self.client.get(url)
        self.assertResponse(response,
            must_not_contain=("<head>", "<title>", "</body>", "</html>")
        )
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

    def test_clean_cache_for_non_render(self):
        """
        headfiles without render a colorscheme, should also cleanup cache file ;)
        """
        self.headfile1.render = False
        self.headfile1.content = "one"
        self.headfile1.save()
        url = self.headfile1.get_absolute_url()
        self.assertTrue("/PyLucid_cache/" in url)
        response = self.client.get(url)
        self.assertEqual(response.content, "one")

        self.headfile1.content = "two"
        self.headfile1.save()
        url = self.headfile1.get_absolute_url()
        self.assertTrue("/PyLucid_cache/" in url)
        response = self.client.get(url)
        self.assertEqual(response.content, "two")

    def test_past_existing_colors(self):
        old_content = self.headfile1.content
        response = self.client.post(self.url_edit_headfile,
            data={
                "filepath": self.headfile1.filepath,
                "_continue": "",
                "render": 1,
                'sites': 1,
                "content": self.YELLOW_STYLES,
            }
        )
        self.assertRedirect(response, status_code=302,
            url="http://testserver" + self.url_edit_headfile
        )
        response = self.client.get(self.url_edit_headfile)
        self.assertResponse(response,
            must_contain=(
                "Merge colors with colorscheme &quot;yellow&quot; (score: 2, tested 2 colorschemes)",
                old_content,
                "was changed successfully. You may edit it again below.",
            ),
            must_not_contain=("Traceback", "created in colorscheme")
        )

        # Check if colors created
        self.assertEqual(Color.objects.all().filter(colorscheme=self.colorscheme1).count(), 2)
        self.assertEqual(Color.objects.all().filter(colorscheme=self.colorscheme2).count(), 2)

        # The headfile content should not changed
        self.headfile1 = EditableHtmlHeadFile.objects.get(pk=self.headfile1.pk)
        self.assertEqual(self.headfile1.content, old_content)

        # The rendered styles should not changed
        self.check_styles()

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
                'name="name" type="text" value="yellow" />',

                # colors:
                'name="color_set-0-name" type="text" value="background" />',
                'name="color_set-0-value" style="background-ColorValue:#222200;" type="text" value="222200" />',
                'name="color_set-1-name" type="text" value="foreground" />',
                'name="color_set-1-value" style="background-ColorValue:#aaaa00;" type="text" value="aaaa00" />',
            ),
            must_not_contain=("Traceback",)
        )

    def test_merge_colors(self):
        Color.objects.create(name="existing_red", value="ff0000", colorscheme=self.colorscheme1)
        Color.objects.create(name="existing_green", value="00ff00", colorscheme=self.colorscheme2)
        self.headfile1.content += "old: #0000Ff; existing_red: #F00; existing_green: #0f0; new: #f0f;"
        self.headfile1.save()

        self.assertEqual(self.headfile1.content,
            "* { color: {{ foreground }}; }\r\nbody { background: {{ background }}; }"
            "old: {{ foreground }}; existing_red: {{ existing_red }}; existing_green: {{ existing_green }}; new: {{ fuchsia }};"
        )

        response = self.request_style(self.design1)
        self.assertEqual(response.content,
            self.YELLOW_STYLES + "old: #aaaa00; existing_red: #ff0000; existing_green: #00ff00; new: #ff00ff;"
        )
        response = self.request_style(self.design2)
        self.assertEqual(response.content,
            self.BLUE_STYLES + "old: #0000ff; existing_red: #ff0000; existing_green: #00ff00; new: #ff00ff;"
        )
        response = self.request_style(self.design3)
        self.assertEqual(response.content, self.INVERTED_BLUE_STYLES)
        response = self.request_style(self.design4)
        self.assertEqual(response.content, self.INVERTED_YELLOW_STYLES)

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
                "Merge colors with colorscheme &quot;yellow&quot; (score: -1, tested 2 colorschemes)",
                "Colors &quot;red:ff0000&quot; created in colorscheme &quot;yellow&quot;",
                "Colors &quot;red:ff0000&quot; created in colorscheme &quot;blue&quot;",

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
        self.assertDOM(response,
            must_contain=(
                # colorscheme name:
                '<input name="name" value="yellow" class="vTextField" maxlength="255" type="text" id="id_name" />',
                #colors:
                '<input name="color_set-0-name" value="background" class="vTextField" maxlength="128" type="text" id="id_color_set-0-name" />',
                '<input style="background-ColorValue:#222200;" name="color_set-0-value" value="222200" maxlength="6" type="text" id="id_color_set-0-value" />',
                '<input name="color_set-0-name" value="background" class="vTextField" maxlength="128" type="text" id="id_color_set-0-name" />',
                '<input style="background-ColorValue:#0000ff;" name="color_set-1-value" value="0000ff" maxlength="6" type="text" id="id_color_set-1-value" />',
            )
        )
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid - Change color scheme</title>',
                'colorpicker.css', 'colorpicker.js',
                'Change color scheme',
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
                'name="name" type="text" value="yellow" />',

                # colors:
                'name="color_set-0-name" type="text" value="hintergrund" />',
                'name="color_set-0-value" style="background-ColorValue:#222200;" type="text" value="222200" />',
                'name="color_set-1-name" type="text" value="vordergrund" />',
                'name="color_set-1-value" style="background-ColorValue:#aaaa00;" type="text" value="aaaa00" />',
            ),
            must_not_contain=("Traceback", "This field is required.")
        )

        # Check sended styles, they must be the same
        self.check_styles()

    def test_remove_unused_colors(self):
        c = Color.objects.create(name="unused1", value="ffffff", colorscheme=self.colorscheme1)

#        cleanup_url = reverse("admin:pylucid_colorscheme_change", args=(self.colorscheme1.pk,))
        response = self.client.get(self.url_edit_colorscheme1 + "cleanup/")
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
                'existing colors: &quot;foreground&quot;, &quot;background&quot;',
                'remove 1 colors: &quot;unused1&quot;',

                # colorscheme name:
                'name="name" type="text" value="yellow" />',

                # colors:
                'name="color_set-0-name" type="text" value="background" />',
                'name="color_set-0-value" style="background-ColorValue:#222200;" type="text" value="222200" />',
                'name="color_set-1-name" type="text" value="foreground" />',
                'name="color_set-1-value" style="background-ColorValue:#aaaa00;" type="text" value="aaaa00" />',
            ),
            must_not_contain=("Traceback", "This field is required.")
        )

        self.check_styles()

    def test_new_render_headfile(self):
        url = reverse("admin:pylucid_editablehtmlheadfile_add")
        response = self.client.post(url,
            data={
                '_continue': 'Save and continue editing',
                 'content': '#00ff00;',
                 'filepath': 'new_without_design.css',
                 'render': 'on'
            },
            follow=True,
        )
        self.assertResponse(response,
            must_contain=(
                "This headfile can't be rendered, because it's not used in a design witch has a colorscheme!"
            ),
            must_not_contain=(
                "Traceback",
                "was added successfully"
            )
        )

    def test_new_headfile(self):
        """
        Two tests: Create a non-render headfile and assign it to a colorscheme design
        """
        url = reverse("admin:pylucid_editablehtmlheadfile_add")
        response = self.client.post(url,
            data={
                '_continue': 'Save and continue editing',
                 'content': '#00ff00;',
                 'filepath': 'new_headfile.css',
            },
            follow=True,
        )
        self.assertResponse(response,
            must_contain=(
                "The editable html head file &quot;new_headfile.css&quot; was added successfully. You may edit it again below.",
                '<input id="id_render" name="render" type="checkbox" />',
                "#00ff00;</textarea>",
            ),
            must_not_contain=("Traceback",)
        )

        headfile = EditableHtmlHeadFile.objects.get(filepath="new_headfile.css")
        headfile_url = headfile.get_absolute_url()
        response = self.client.get(headfile_url)
        self.assertEqual(response.content, "#00ff00;")

        # Add the new headfile to a design with colorscheme and change the color value:

        self.design1.headfiles.add(headfile)

        url = reverse("admin:pylucid_editablehtmlheadfile_change", args=(headfile.id,))
        response = self.client.post(url,
            data={
                '_continue': 'Save and continue editing',
                 'content': '#00ffff;',
                 'filepath': 'new_headfile.css',
                 'render': 'on'
            },
            follow=True,
        )
        # The color value must be replace with a named color:
        self.assertResponse(response,
            must_contain=(
                "Colors &quot;cyan:00ffff&quot; created in colorscheme &quot;yellow&quot;",
                "The editable html head file &quot;new_headfile.css&quot; was changed successfully. You may edit it again below.",
                '<input checked="checked" id="id_render" name="render" type="checkbox" />',
                "{{ cyan }};</textarea>",
            ),
            must_not_contain=("Traceback",)
        )
        headfile = EditableHtmlHeadFile.objects.get(filepath="new_headfile.css") # renew object
        headfile_url = headfile.get_absolute_url(self.colorscheme1)

        response = self.client.get(headfile_url)
        # The cache file should be updated:
        self.assertEqual(response.content, "#00ffff;")



if __name__ == "__main__":
    # Run all unittest directly

    tests = __file__
#    tests = "pylucid_plugins.design.tests.SwitchDesignTest"

    management.call_command('test', tests,
        verbosity=2,
#        failfast=True
    )
