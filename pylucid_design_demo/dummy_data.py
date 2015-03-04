# coding: utf-8

"""
    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
from cms import constants
from django.contrib.auth.models import User
from cms.models import Placeholder
from cms.api import create_page, add_plugin, get_page_draft
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

PAGE_COUNTS = [4,2,3,1]


def create_placeholder(dummy_text):
    placeholder = Placeholder.objects.create(slot="content")
    placeholder.save()
    add_plugin(placeholder, "DesignSwitchPlugin", settings.LANGUAGE_CODE)
    add_plugin(placeholder, "TextPlugin", settings.LANGUAGE_CODE, body=dummy_text)
    return placeholder


def create_dummy_page(title, template, placeholder, parent=None):
    page = create_page(
        title, template,
        language=settings.LANGUAGE_CODE,
        parent=parent,
        in_navigation=True,
    )
    page = get_page_draft(page)
    page.placeholders.add(placeholder)
    page.publish(settings.LANGUAGE_CODE)

    print("\t%s" % page.get_absolute_url(language=settings.LANGUAGE_CODE))
    return page

def create_tree(placeholder, title="level", parent=None, level=1):
    for no in range(1, PAGE_COUNTS[level-1]+1):
        page_title = "%s %s" % (title, no)
        page = create_dummy_page(page_title, constants.TEMPLATE_INHERITANCE_MAGIC, placeholder, parent)
        if level<len(PAGE_COUNTS):
            create_tree(placeholder, page_title, parent=page, level=level+1)


def create_pages():
    print(" *** Create pages *** ")

    placeholder = create_placeholder(SOURCE_DUMMY_TEXT)

    create_tree(placeholder)

    # Add a sitemap page
    placeholder = Placeholder.objects.create(slot="content")
    placeholder.save()
    add_plugin(placeholder, "HtmlSitemapPlugin", settings.LANGUAGE_CODE)
    create_dummy_page("sitemap", constants.TEMPLATE_INHERITANCE_MAGIC, placeholder)


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