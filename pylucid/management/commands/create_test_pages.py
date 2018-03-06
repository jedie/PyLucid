#!/usr/bin/env python3

from django.conf import settings
from django.core.management import BaseCommand

# https://github.com/jedie/django-cms-tools
from django_cms_tools.fixtures.pages import CmsPageCreator


class TestPageCreator(CmsPageCreator):
    def __init__(self, template_file, template_name, *args, **kwargs):
        self.template = template_file
        self.template_name = template_name

        super().__init__(*args, **kwargs)

    def get_title(self, language_code, lang_name):
        return self.template_name


class Command(BaseCommand):
    def handle(self, **options):
        for template_file, template_name in settings.CMS_TEMPLATES:
            TestPageCreator(template_file, template_name).create()
