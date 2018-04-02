# coding: utf-8

"""
    PyLucid
    ~~~~~~~

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import unicode_literals
from cmsplugin_markup.models import MarkupField
from django.test import TestCase


class CMSPluginMarkupTest(TestCase):
    def test_textile(self):
        instance = MarkupField.objects.create(body="Markdown: äöüß", markup="markdown")
        self.assertEqual(instance.body_html, "<p>Markdown: äöüß</p>")

    def test_markdown(self):
        instance = MarkupField.objects.create(body="Textile äöüß", markup="textile")
        self.assertEqual(instance.body_html, "\t<p>Textile äöüß</p>")

    def test_restructuredtext(self):
        instance = MarkupField.objects.create(body="ReSt: äöüß",markup="restructuredtext")
        self.assertEqual(instance.body_html,'<p>ReSt: äöüß</p>\n')

    def test_creole(self):
        instance = MarkupField.objects.create(body="Creole - äöüß", markup="creole")
        self.assertEqual(instance.body_html, "<p>Creole - äöüß</p>")