# coding: utf-8

"""
    cmsplugin markup itegration tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :created: 2015 by JensDiemer.de
    :modified: 2018 by Jens Diemer
    :copyleft: 2015-2018 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.test import TestCase


class CMSPluginMarkupTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # We can't normal import this, because:
        # pylucid/tests/test_cmsplugin_markup.py:13: in <module>
        #     from cmsplugin_markup.models import MarkupField
        # ../cmsplugin-markup/cmsplugin_markup/models.py:9: in <module>
        #     from cms.models import CMSPlugin
        # ../../lib/python3.6/site-packages/cms/models/__init__.py:2: in <module>
        #     from .settingmodels import *  # nopyflakes
        # ../../lib/python3.6/site-packages/cms/models/settingmodels.py:9: in <module>
        #     class UserSettings(models.Model):
        # ../../lib/python3.6/site-packages/cms/models/settingmodels.py:10: in UserSettings
        #     user = models.OneToOneField(settings.AUTH_USER_MODEL, editable=False, related_name='djangocms_usersettings')
        # ../../lib/python3.6/site-packages/django/conf/__init__.py:56: in __getattr__
        #     self._setup(name)
        # ../../lib/python3.6/site-packages/django/conf/__init__.py:39: in _setup
        #     % (desc, ENVIRONMENT_VARIABLE))
        # E   django.core.exceptions.ImproperlyConfigured: Requested setting AUTH_USER_MODEL, but settings are not configured...
        from cmsplugin_markup.models import MarkupField
        cls.MarkupField = MarkupField


    def test_textile(self):
        instance = self.MarkupField.objects.create(body="Markdown: äöüß", markup="markdown")
        self.assertEqual(instance.body_html, "<p>Markdown: äöüß</p>")

    def test_markdown(self):
        instance = self.MarkupField.objects.create(body="Textile äöüß", markup="textile")
        self.assertEqual(instance.body_html, "\t<p>Textile äöüß</p>")

    def test_restructuredtext(self):
        instance = self.MarkupField.objects.create(body="ReSt: äöüß",markup="restructuredtext")
        self.assertEqual(instance.body_html,'<p>ReSt: äöüß</p>\n')

    def test_creole(self):
        instance = self.MarkupField.objects.create(body="Creole - äöüß", markup="creole")
        self.assertEqual(instance.body_html, "<p>Creole - äöüß</p>")
