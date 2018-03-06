#!/usr/bin/env python3

from django.conf import settings
from django.core.management import BaseCommand

# https://github.com/jedie/django-cms-tools
from django_cms_tools.fixtures.pages import CmsPageCreator, DummyPageGenerator


class SubPageGenerator(DummyPageGenerator):
    def __init__(self, parent_page, *args, **kwargs):
        self.parent_page = parent_page

        super().__init__(*args, **kwargs)

    def get_parent_page(self):
        if self.current_level == 1:
            return self.parent_page
        return super().get_parent_page()


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
            page, created = TestPageCreator(template_file, template_name).create()
            if created:
                SubPageGenerator(parent_page=page, title_prefix=template_name).create()
