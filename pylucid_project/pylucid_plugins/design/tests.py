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

from django.core.urlresolvers import reverse

from dbtemplates.models import Template as DBTemplateModel

from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid.models import PageMeta, Design, \
                                EditableHtmlHeadFile, ColorScheme, Color


class CloneDesignTestCase(basetest.BaseUnittest):
    def _pre_setup(self, *args, **kwargs):
        super(CloneDesignTestCase, self)._pre_setup(*args, **kwargs)

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

        self.failUnless(
            Design.objects.filter(name__exact=new_name).count() == 1
        )
        self.failUnless(
            ColorScheme.objects.filter(name__exact=new_name).count() == 1
        )
        self.failUnless(
            EditableHtmlHeadFile.objects.filter(filepath__startswith="%s/" % new_name).count() > 0
        )
        self.failUnless(
            DBTemplateModel.objects.filter(name__exact="%s.html" % new_name).count() == 1
        )


#------------------------------------------------------------------------------


SOURCE_CSS = """.foo { color: #ffffff; background-color: #000000;}
.bar { color: #ff0000; background-color: #ffff00;}"""

DEST_CSS = """.foo { color: {{ white }}; background-color: {{ black }};}
.bar { color: {{ red }}; background-color: {{ yellow }};}"""


class ColorSchemeTestCase(basetest.BaseUnittest):
    """
    TODO: created more tests, for colors.
    """
    def _pre_setup(self, *args, **kwargs):
        super(ColorSchemeTestCase, self)._pre_setup(*args, **kwargs)

        self.test_colorscheme = ColorScheme.on_site.all()[0]
        self.test_design = Design.objects.filter(colorscheme=self.test_colorscheme)[0]
        for headfile in self.test_design.headfiles.all():
            if headfile.render:
                self.test_headfile = headfile
                break

        self.login("superuser")

    def _clean_cache_file(self):
        cachepath = self.test_headfile.get_cachepath(self.test_colorscheme)
        if os.path.isfile(cachepath):
            print "remove cache file: %r" % cachepath
            print file(cachepath).read()
            os.remove(cachepath)
        else:
            print "cache file not exists: %r" % cachepath

    def test_auto_rename(self):
        """
        TODO: Check if colors really renamed ;)
        """
        colorscheme_id = ColorScheme.on_site.all()[0].id
        url = reverse("Design-rename_colors", args=(colorscheme_id,))
        response = self.client.get(url)
        new_url = "http://testserver/admin/pylucid/colorscheme/1/"
        self.assertRedirect(response, url=new_url, status_code=302)


    def test_create_new_colors(self):
        """
        FIXME: The cachefile would be not updated in unittest. 
        But i can't reproduced it in real environment!
        """
        Color.objects.filter(colorscheme=self.test_colorscheme).delete()

        url = reverse(
            "admin:pylucid_editablehtmlheadfile_change",
            args=(self.test_headfile.id,)
        )
        response = self.client.post(url,
            data={
                "filepath": self.test_headfile.filepath,
                "_continue": "",
                "render": 1,
                'sites': 1,
                "content": SOURCE_CSS,
            }
        )
        self.assertRedirect(response, status_code=302,
            url="http://testserver" + url
        )
        response = self.client.get(url)
        self.assertResponse(response,
            must_contain=(
                "1 colorscheme updated. 4 colors created. 0 colors updated.",
                DEST_CSS,
                "was changed successfully. You may edit it again below.",
                "EditableHtmlHeadFile cached successful into",
            ),
            must_not_contain=("Traceback",)
        )

        colors = Color.objects.filter(colorscheme=self.test_colorscheme)
        self.failUnlessEqual(colors.count(), 4)

        # Check headfile send view:
        "/headfile/initial_site_style/main.css?ColorScheme=1"
        headfile_view_url = reverse(
            "PyLucid-send_head_file", args=(self.test_headfile.filepath,)
        )
        headfile_view_url += "?ColorScheme=%i" % self.test_colorscheme.id
        response = self.client.get(headfile_view_url)
        self.assertResponse(response,
            must_contain=(SOURCE_CSS,),
            must_not_contain=("Traceback",)
        )

#        self._clean_cache_file() # XXX

        headfile_url = self.test_headfile.get_absolute_url(self.test_colorscheme)

        # Check if the headfile was cached
        self.assertTrue("/headfile_cache/" in headfile_url)

        # Low level test (renew object needed):
        self.test_headfile = EditableHtmlHeadFile.objects.get(pk=self.test_headfile.pk)
        self.failUnlessEqual(self.test_headfile.content, DEST_CSS)
        self.failUnlessEqual(self.test_headfile.get_rendered(self.test_colorscheme), SOURCE_CSS)

        # Check if headfile url is in a page that's used the headfile
        pagemeta = PageMeta.objects.filter(pagetree__design=self.test_design)[0]
        url = pagemeta.get_absolute_url()
        response = self.client.get(url)
        self.assertResponse(response,
            must_contain=(
                '<link href="%s" rel="stylesheet" type="text/css" />' % headfile_url,
            ),
            must_not_contain=("Traceback",)
        )

        "/media/PyLucid/headfile_cache/ColorScheme_1/initial_site_style/main.css"

        # request the rendered css file:
        response = self.client.get(headfile_url)
        self.assertResponse(response,
            must_contain=(SOURCE_CSS,),
            must_not_contain=("Traceback",)
        )







if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management
    management.call_command('test', "pylucid_plugins.design.tests.ColorSchemeTestCase",
#        verbosity=0,
        verbosity=1,
        failfast=True
    )
#    management.call_command('test', __file__,
#        verbosity=1,
##        verbosity=0,
##        failfast=True
#    )
