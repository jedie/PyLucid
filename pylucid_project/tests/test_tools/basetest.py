# coding: utf-8


"""
    PyLucid unittest base class
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2009-2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import os
import re
import sys


if __name__ == "__main__":
    # Run all unittest directly

#     tests = __file__
    tests = "pylucid_plugins.auth.tests"
#     tests = "pylucid_plugins.auth.tests.LoginTest.test_login_ajax_form"

    from pylucid_project.tests import run_test_directly
    run_test_directly(tests,
        verbosity=2,
#        failfast=True,
        failfast=False,
    )
    sys.exit()


from django import forms
from django.conf import settings
from django.contrib.messages import constants as message_constants
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.test import TestCase
from django.utils.html import conditional_escape

from django_tools.unittest_utils.unittest_base import BaseTestCase

from pylucid_project.apps.pylucid.models import PageTree, Language, EditableHtmlHeadFile


supported_languages = dict(settings.LANGUAGES)


class BaseUnittest(BaseTestCase, TestCase):
    fixtures = [
        # Special test users:
        os.path.join(settings.PYLUCID_BASE_PATH, "tests/fixtures/test_users.json"),
        # The normal base install fixtures:
        os.path.join(settings.PYLUCID_BASE_PATH, "apps/pylucid_admin/fixtures/pylucid.json"),
    ]

    def _pre_setup(self, *args, **kwargs):
        super(BaseUnittest, self)._pre_setup(*args, **kwargs)

        # fixtures loaded?
        for fixture in self.fixtures:
            self.failUnless(os.path.isfile(fixture), "Test fixture file %r not found!" % fixture)

        if Language.objects.count() < 2:
            raise SystemExit("Languages not exist! test_users.json fixtures not loaded?")

        if PageTree.objects.count() == 0:
            raise SystemExit("PyLucid initial data fixtures not loaded!")

        # Remove the real Pygments CSS content, because it contains the
        # String "Traceback" which used in many tests.
        # If django-compressor not work or disabled, the CSS content would be insert inline.
        pygments_css = EditableHtmlHeadFile.objects.get(filepath="pygments.css")
        pygments_css.content = "Pygments CSS Content (removed by %s)" % __file__
        pygments_css.save()

        # Fill PyLucid own UserProfile with SHA password data
        for usertype, data in self.TEST_USERS.iteritems():
            user = self._get_user(usertype)
            user.set_password(data["password"])

    def easy_create(self, ModelClass, defaults, **kwargs):
        """
        Create new model instances with defaults.
        used e.g. in blog/lexicon plugin tests
        """
        create_data = defaults
        create_data.update(kwargs)
        instance = ModelClass(**create_data)
        instance.save()
        return instance

    def assertPyLucidPermissionDenied(self, response):
        """ Test if response is a PyLucid permission deny page """
        self.assertStatusCode(response, excepted_code=403)
        self.assertResponse(response,
            must_contain=("<h1>403 Forbidden</h1>",),
            must_not_contain=("Traceback",)
        )

    def assertAdminLoginPage(self, response):
        """
        Check if the response is the django login page
        with PyLucid modifications
        """
        url = response.request["PATH_INFO"]

        # XXX: work-a-round for: https://github.com/gregmuellegger/django/issues/1
        response.content = re.sub(
            "js_sha_link(\+*)='(.*?)'",
            "js_sha_link\g<1>='XXX'",
            response.content
        )
        self.assertDOM(response,
            must_contain=(
                '<input id="id_username" maxlength="254" name="username" type="text" />',
                '<input id="id_password" name="password" type="password" />',
                '<input type="submit" value="Log in" />',
            )
        )

        self.assertResponse(response,
            must_contain=(
                # django
                '<form action="%s" method="post" id="login-form">' % url,

                # from pylucid:
                'JS-SHA-Login',
                "Do really want to send your password in plain text?",
            ),
            must_not_contain=("Traceback",)
        )
        self.assertStatusCode(response, 200)

    def assertAtomFeed(self, response, language_code):
        # application/atom+xml; charset=utf8 -> application/atom+xml
        content_type = response["content-type"].split(";", 1)[0]
        self.failUnlessEqual(content_type, "application/atom+xml")

        self.failUnlessEqual(response["content-language"], language_code)
        self.assertResponse(response,
            must_contain=(
                '<?xml version="1.0" encoding="utf-8"?>',
                '<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="%s">' % language_code,
                "</feed>",
            ),
            must_not_contain=(
                "Traceback",
                "<rss", "<body>", "<html>"
            )
        )

    def assertRssFeed(self, response, language_code):
        # application/rss+xml; charset=utf8 -> application/rss+xml
        content_type = response["content-type"].split(";", 1)[0]
        self.failUnlessEqual(content_type, "application/rss+xml")

        self.failUnlessEqual(response["content-language"], language_code)
        self.assertResponse(response,
            must_contain=(
                '<?xml version="1.0" encoding="utf-8"?>',
                '<rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">',
                '<language>%s</language>' % language_code,
                "</rss>",
            ),
            must_not_contain=(
                "Traceback",
                "<feed", "<body>", "<html>"
            )
        )

    def login(self, usertype):
        """
        Login test user and add him to the current site.
        """
        user = super(BaseUnittest, self).login(usertype)

        site = Site.objects.get_current()

        from pylucid_project.apps.pylucid.models import UserProfile
        try:
            userprofile = user.get_profile()
        except UserProfile.DoesNotExist:
            # FIXME: Why does in some case user.get_profile() not work???
            userprofile = UserProfile.objects.get(user=user)

        if not site in userprofile.sites.all():
            print "Info: Add user to site %s" % site
            userprofile.sites.add(site)

        return user

    def login_with_permissions(self, usertype, permissions):
        """ login user and add given permissions """
        user = self.login(usertype)
        self.add_user_permissions(user, permissions=permissions)
        return user


class BaseLanguageTestCase(BaseUnittest):
    """
    Contains some language helper stuff.    
    """
    def tearDown(self):
        super(BaseLanguageTestCase, self).tearDown()
        if self._system_preferences is not None:
            # revert changes from self.enable_i18n_debug()
            self._system_preferences["message_level_anonymous"] = self.old_message_level
            self._system_preferences.save()
        settings.DEBUG = False
        settings.PYLUCID.I18N_DEBUG = False

    def enable_i18n_debug(self):
        """
        enable DEBUG, PYLUCID.I18N_DEBUG and set message_level_anonymous to DEBUG.
        """
        cache.clear()
        from pylucid_project.apps.pylucid.preference_forms import SystemPreferencesForm
        self._system_preferences = SystemPreferencesForm()
        self.old_message_level = self._system_preferences["message_level_anonymous"]
        self._system_preferences["message_level_anonymous"] = message_constants.DEBUG
        self._system_preferences.save()
        settings.DEBUG = True
        settings.PYLUCID.I18N_DEBUG = True

    def _pre_setup(self, *args, **kwargs):
        """ create some language related attributes """
        super(BaseLanguageTestCase, self)._pre_setup(*args, **kwargs)

        self._system_preferences = None  # used in enable_i18n_debug() and tearDown()

        # default language is defined with settings.LANGUAGE_CODE
        self.default_language = Language.objects._get_default_language()
        self.failUnlessEqual(self.default_language.code, settings.LANGUAGE_CODE)

        self.other_lang_code = "de"
        assert self.other_lang_code != self.default_language.code
        self.other_language = Language.objects.get(code=self.other_lang_code)

    def assertContentLanguage(self, response, lang):
        """ Check if response is in right language """
        assert isinstance(lang, Language)
        is_lang = response["content-language"]
        if is_lang != lang.code:
            self.raise_browser_traceback(response,
                msg="Header 'Content-Language' is not %r it's: %r" % (lang.code, is_lang)
            )
        self.assertResponse(response,
            must_contain=(
                '<body lang="%s">' % lang.code,
                '<html lang="%(code)s">' % {
                    "code": lang.code
                },
            )
        )


class BaseMoreLanguagesTestCase(BaseLanguageTestCase):
    """
    For tests with more existing languages
    """
    def _pre_setup(self, *args, **kwargs):
        super(BaseMoreLanguagesTestCase, self)._pre_setup(*args, **kwargs)

        self.codes = ("es", "es-ar", "pt", "hr")
        self.languages = {}
        for code in self.codes:
            new_language = Language(
                code=code, description=supported_languages[code]
            )
#            print "test language %r created." % new_language
            new_language.save()
            self.languages[code] = new_language


class MarkupTestHelper(object):
    def _prepare_text(self, txt):
        """
        prepare the multiline, indentation text.
        from https://github.com/jedie/python-creole/blob/master/tests/utils/utils.py
        """
        txt = unicode(txt)
        txt = txt.splitlines()
        assert txt[0] == "", "First must be empty!"
        txt = txt[1:]  # Skip the first line

        # get the indentation level from the first line
        count = False
        for count, char in enumerate(txt[0]):
            if char != " ":
                break

        assert count != False, "second line is empty!"

        # remove indentation from all lines
        txt = [i[count:].rstrip(" ") for i in txt]

        # ~ txt = re.sub("\n {2,}", "\n", txt)
        txt = "\n".join(txt)

        # strip *one* newline at the begining...
        if txt.startswith("\n"): txt = txt[1:]
        # and strip *one* newline at the end of the text
        if txt.endswith("\n"): txt = txt[:-1]
        # ~ print repr(txt)
        # ~ print "-"*79

        return txt


if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management

    tests = __file__
#    tests = "pylucid_plugins.page_admin.tests.PageAdminTest.test_translate_form"

    management.call_command('test', tests,
        verbosity=2,
        failfast=True
    )
