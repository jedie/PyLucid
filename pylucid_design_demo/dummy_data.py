# coding: utf-8

"""
    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
from django.contrib.auth.models import User
from cms.models import Placeholder
from cms.api import create_page, add_plugin
from django.conf import settings

SOURCE_DUMMY_TEXT = (
    "<p>Lorem ipsum dolor sit amet, consectetur adipisici elit, sed eiusmod tempor incidunt"
    " ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud"
    " exercitation ullamco laboris nisi ut aliquid ex ea commodi consequat. Quis aute"
    " iure reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
    " Excepteur sint obcaecat cupiditat non proident, sunt in culpa qui officia deserunt"
    " mollit anim id est laborum.</p>"
)
SOURCE_DUMMY_TEXT = SOURCE_DUMMY_TEXT * 3

TEST_USERNAME="test"
TEST_USERPASS="12345678"

LEVEL1_COUNT=3
LEVEL2_COUNT=2

def create_dummy_page(title, template, dummy_text, parent=None):
    page = create_page(
        title, template,
        language=settings.LANGUAGE_CODE,
        parent=parent,
        in_navigation=True,
    )
    placeholder = Placeholder.objects.create(slot="content")
    placeholder.save()
    page.placeholders.add(placeholder)
    placeholder.page = page

    add_plugin(placeholder, "TextPlugin", settings.LANGUAGE_CODE, body=dummy_text)

    page.publish(settings.LANGUAGE_CODE)

    print("\t%s" % page.get_absolute_url(language=settings.LANGUAGE_CODE))

    return page


def create_pages():
    for template_path, template_name in settings.CMS_TEMPLATES:
        print(" *** Create page %r *** " % template_name)

        dummy_text = SOURCE_DUMMY_TEXT
        parent = create_dummy_page(template_name, template_path, dummy_text)

        for level1 in range(1, LEVEL1_COUNT+1):
            for level2 in range(1, LEVEL2_COUNT+2):
                title="level %i.%i" % (level1, level2)
                dummy_text = "<h2>%s</h2>%s" % (title, SOURCE_DUMMY_TEXT)
                page = create_dummy_page(title, template_path, dummy_text, parent)
            parent=page


def create_test_user():
    user, created = User.objects.get_or_create(username=TEST_USERNAME)
    user.is_staff=True
    user.is_superuser=True
    user.set_password(TEST_USERPASS)
    user.save()


if __name__ == "__main__":
    # local test

    import django
    os.environ['DJANGO_SETTINGS_MODULE'] = 'pylucid_design_demo.settings'
    django.setup()

    from django.core.management import call_command
    # call_command("migrate")
    create_pages()