#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    :copyleft: 2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid.models import PageTree, PageContent
from pylucid_project.apps.pylucid.markup import MARKUP_HTML


class IncludeTest(basetest.BaseLanguageTestCase):
    """
    inherited from BaseUnittest:
        - initial data fixtures with default test users
        - self.login()
    
    inherited from BaseLanguageTest:
        - self.default_language - system default Language model instance (default: en instance)
        - self.default_language - alternative language code than system default (default: 'de')
        - self.other_language - alternative Language mode instance (default: de instance)
        - assertContentLanguage() - Check if response is in right language
    """
    def _pre_setup(self, *args, **kwargs):
        super(IncludeTest, self)._pre_setup(*args, **kwargs)

        pagetree = PageTree.objects.get_root_page(user=AnonymousUser())
        self.pagecontent = PageContent.objects.get(
            pagemeta__pagetree=pagetree, pagemeta__language=self.default_language
        )
        self.pagecontent.markup = MARKUP_HTML
        self.url = self.pagecontent.get_absolute_url()

        self.pylucid_js_tools_filepath = os.path.join(settings.STATIC_ROOT, "PyLucid", "pylucid_js_tools.js")

    def setUp(self):
        self.old_DEBUG = settings.DEBUG
        settings.DEBUG = True

    def tearDown(self):
        settings.DEBUG = self.old_DEBUG

    def _set_content(self, text):
        self.pagecontent.content = (
            "<p>%(pre)s</p>\n"
            "%(text)s\n"
            "<p>%(post)s</p>"
        ) % {
            "pre": "*" * 80,
            "text": text,
            "post": "^" * 80,
        }
        self.pagecontent.save()

    def _test(self, lucidtag, must_contain, must_not_contain=()):
        must_not_contain = (
            "Traceback", "XXX INVALID TEMPLATE STRING",
            "Form errors", "field is required",
        ) + must_not_contain

        self._set_content(lucidtag)
        response = self.client.get(self.url)
        self.assertResponse(response,
            must_contain=must_contain,
            must_not_contain=must_not_contain,
        )

    def test_local_file_basic(self):
#        self.login("superuser") # For seeing verbose error messages
        self._test(
            '{%% lucidTag include.local_file filepath="%s" %%}' % self.pylucid_js_tools_filepath,
            must_contain=(
                '// helper function for console logging',
            ),
            must_not_contain=(
                "Traceback", "XXX INVALID TEMPLATE STRING",
                "Form errors", "field is required",
                "pygments_code", '<span class="c1">'
            )
        )

    def test_local_file_highlight(self):
#        self.login("superuser") # For seeing verbose error messages
        self._test(
            '{%% lucidTag include.local_file filepath="%s" highlight="js" %%}' % self.pylucid_js_tools_filepath,
            must_contain=(
                '<fieldset class="pygments_code">',
                '<legend class="pygments_code">JavaScript</legend>',
                '<span class="c1">// helper function for console logging</span>'
            )
        )

    def test_local_file_highlight_autodetection(self):
#        self.login("superuser") # For seeing verbose error messages
        self._test(
            '{%% lucidTag include.local_file filepath="%s" highlight=True %%}' % self.pylucid_js_tools_filepath,
            must_contain=(
                '<fieldset class="pygments_code">',
                '<legend class="pygments_code">JavaScript</legend>',
                '<span class="c1">// helper function for console logging</span>'
            )
        )

    def test_local_file_base_path(self):
        self.login("superuser") # For seeing verbose error messages
        self._test(
            '{% lucidTag include.local_file filepath="/etc/passwd" %}',
            must_contain=(
                'Filepath doesn&#39;t start with',
                '[Include error.]',
            )
        )

    def test_local_file_base_path_error(self):
        """ Normal users should not see the verbose error """
        self._test(
            '{% lucidTag include.local_file filepath="/etc/passwd" %}',
            must_contain=('[Include error.]',),
            must_not_contain=('Filepath doesn&#39;t start with',)
        )

    def test_local_file_markup(self):
        self.login("superuser") # For seeing verbose error messages

        base_path = os.path.normpath(os.path.join(settings.PYLUCID_BASE_PATH, ".."))

        old_basepath = settings.PYLUCID_INCLUDE_BASEPATH
        settings.PYLUCID_INCLUDE_BASEPATH = base_path

        filepath = os.path.join(base_path, "README.creole")

        self._test(
            '{%% lucidTag include.local_file filepath="%s" markup="creole" %%}' % filepath,
            must_contain=(
                '''<a href="?lexicon=PyLucid CMS" title="lexicon entry 'PyLucid CMS' - PyLucid is the CMS thats built this page." class="PyLucidPlugins lexicon openinwindow">PyLucid</a> is an Open Source web content management system written in Python using <a href="http://www.pylucid.org/permalink/41/dependencies-and-copyrights">Django, jQuery and many more external software...</a></p>''',
                '<li>Open Source (GPL v3 or later)</li>',
                '<li>Multi site support (Allows a single installation to serve multiple websites.)</li>'
            ),
            must_not_contain=(
                '[Include error.]',
                'Filepath doesn&#39;t start with',
                'Can&#39;t read file',
            )
        )
        settings.PYLUCID_INCLUDE_BASEPATH = old_basepath

    def test_local_file_markup_and_highlight(self):
        self.login("superuser") # For seeing verbose error messages

        base_path = os.path.normpath(os.path.join(settings.PYLUCID_BASE_PATH, ".."))

        old_basepath = settings.PYLUCID_INCLUDE_BASEPATH
        settings.PYLUCID_INCLUDE_BASEPATH = base_path

        filepath = os.path.join(base_path, "README.creole")

        self._test(
            '{%% lucidTag include.local_file filepath="%s" markup="creole" highlight="html" %%}' % filepath,
            must_contain=(
                '<fieldset class="pygments_code">',
                '<legend class="pygments_code">HTML</legend>',
                '<span class="nt">&lt;h1&gt;</span>about PyLucid<span class="nt">&lt;/h1&gt;</span>',
            ),
            must_not_contain=(
                '[Include error.]',
                'Filepath doesn&#39;t start with',
                'Can&#39;t read file',
            )
        )
        settings.PYLUCID_INCLUDE_BASEPATH = old_basepath

    def test_remote_file_basic(self):
        #self.login("superuser") # For seeing verbose error messages
        self._test(
            '{% lucidTag include.remote url="http://www.pylucid.org/permalink/45/a-simple-unicode-test-page" %}',
            must_contain=(
                '&amp;darr;&amp;nbsp;Basic Latin-1 (0x0021-0x007E):',
                'This page would be used for some unittests, too ;)',
                'Latin-1 Supplement (0x0080-0x00FF):',
                'German Umlaute: ä ö ü ß Ä Ö Ü',
            ),
        )

    def test_remote_file_highlight(self):
        #self.login("superuser") # For seeing verbose error messages
        self._test(
            '{% lucidTag include.remote url="http://www.pylucid.org/permalink/45/a-simple-unicode-test-page" highlight="html" %}',
            must_contain=(
                '<fieldset class="pygments_code">',
                '<legend class="pygments_code">HTML</legend>',

                '<span class="ni">&amp;darr;&amp;nbsp;</span>Basic Latin-1 (0x0021-0x007E):',
                'This page would be used for some unittests, too ;)<span class="nt">&lt;/p&gt;</span>',
                '<span class="s">&quot;Latin-1-Supplement-0x0080-0x00FF&quot;</span>',
                '<span class="nt">&lt;p&gt;</span>German Umlaute: ä ö ü ß Ä Ö Ü<span class="nt">&lt;/p&gt;</span>',
            ),
        )


if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management

    tests = __file__
#    tests = "pylucid_plugins.page_admin.tests.ConvertMarkupTest"

    management.call_command('test', tests,
#        verbosity=0,
        verbosity=1,
#        failfast=True
    )

