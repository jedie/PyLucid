# coding: utf-8

"""
    PyLucid unittest base class
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.test import TransactionTestCase
from django.contrib.sites.models import Site

from django_tools.unittest.unittest_base import BaseTestCase

from pylucid.models import Language



class BaseUnittest(BaseTestCase, TransactionTestCase):
    def __init__(self, *args, **kwargs):
        super(BaseUnittest, self).__init__(*args, **kwargs)

        # Get the default lang code from system preferences
        from pylucid.preference_forms import SystemPreferencesForm
        self.system_preferences = SystemPreferencesForm().get_preferences()
        self.default_lang_code = self.system_preferences["lang_code"]
        self.default_lang_entry = Language.objects.get(code=self.default_lang_code)

    def assertContentLanguage(self, response, lang):
        assert isinstance(lang, Language)
        is_lang = response["content-language"]
        if is_lang != lang.code:
            self.raise_browser_traceback(response,
                msg="Header 'Content-Language' is not %r it's: %r" % (lang.code, is_lang)
            )
        self.assertResponse(response,
            must_contain=('<meta name="DC.Language" content="%s">' % lang.code,)
        )

    def login(self, usertype):
        """
        Login test user.
        Add him to the site, otherwise he can't login ;)
        """
        site = Site.objects.get_current()
        user = self._get_user(usertype="normal")

        from pylucid.models import UserProfile
        try:
            userprofile = user.get_profile()
        except UserProfile.DoesNotExist:
            # FIXME: Why does in some case user.get_profile() not work???
            userprofile = UserProfile.objects.get(user=user)

        if not site in userprofile.sites.all():
            print "Info: Add user to site %s" % site
            userprofile.sites.add(site)

        ok = self.client.login(username=self.TEST_USERS[usertype]["username"],
                               password=self.TEST_USERS[usertype]["password"])
        self.failUnless(ok, "Can't login test user '%s'!" % usertype)
        return user

