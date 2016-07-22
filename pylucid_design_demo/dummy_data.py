# coding: utf-8

"""
    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

from django.contrib.auth.models import User
from django.conf import settings

from cms import constants
from cms.models import Placeholder
from cms.api import create_page, add_plugin, get_page_draft


SOURCE_DUMMY_TEXT = (
    "<p>Lorem ipsum dolor sit amet, consectetur adipisici elit, sed eiusmod tempor incidunt"
    " ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud"
    " exercitation ullamco laboris nisi ut aliquid ex ea commodi consequat. Quis aute"
    " iure reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
    " Excepteur sint obcaecat cupiditat non proident, sunt in culpa qui officia deserunt"
    " mollit anim id est laborum.</p>"
)
SOURCE_DUMMY_TEXT = SOURCE_DUMMY_TEXT * 3



SOURCE_DUMMY_TEXT = "<p>Username: <strong>%s</strong> password: <strong>%s</strong>%s" % (
    settings.TEST_USERNAME, settings.TEST_USERPASS, SOURCE_DUMMY_TEXT
)

# PAGE_COUNTS = [4,2,3,1]
PAGE_COUNTS = [3, 2, 1]


def create_placeholder(dummy_text, slot="content"):
    placeholder = Placeholder.objects.create(slot=slot)
    placeholder.save()
    for language in settings.LANGUAGES:
        language_code = language[0]
        add_plugin(placeholder, "TextPlugin", language_code, body=dummy_text)
    placeholder.save()
    return placeholder


def create_dummy_page(title, template, placeholders, parent=None):
    page = create_page(
        title, template,
        language=settings.LANGUAGE_CODE,
        parent=parent,
        in_navigation=True,
        with_revision=True
    )
    for placeholder in placeholders:
        page.placeholders.add(placeholder)

    page = get_page_draft(page)
    page.publish(settings.LANGUAGE_CODE)

    print("\t%s" % page.get_absolute_url(language=settings.LANGUAGE_CODE))
    return page

def create_tree(default_placeholders, title=None, parent=None, level=1):
    pages=[]
    for no in range(1, PAGE_COUNTS[level-1]+1):
        if title is None:
            page_title = "level %s" % no
        else:
            page_title = "%s.%s" % (title, no)

        content_placeholder = create_placeholder(
            "<h2>Dummy page on %s</h2>%s" % (page_title, SOURCE_DUMMY_TEXT)
        )
        placeholders = [content_placeholder] + default_placeholders
        page = create_dummy_page(page_title, constants.TEMPLATE_INHERITANCE_MAGIC, placeholders, parent)
        pages.append(page)
        if level<len(PAGE_COUNTS):
            create_tree(default_placeholders, page_title, parent=page, level=level+1)
    return pages


def create_pages():
    header_praceholder = create_placeholder(
        "<h1>PyLucid Design DEMO</h1>", slot="header"
    )
    default_placeholders = [header_praceholder]

    print(" *** Create pages *** ")
    create_tree(default_placeholders)

    # Add a sitemap page
    placeholder = Placeholder.objects.create(slot="content")
    placeholder.save()
    add_plugin(placeholder, "HtmlSitemapPlugin", settings.LANGUAGE_CODE)
    create_dummy_page("sitemap", constants.TEMPLATE_INHERITANCE_MAGIC, [placeholder])


def create_test_user():
    user, created = User.objects.get_or_create(username=settings.TEST_USERNAME)
    user.is_staff=True
    user.is_superuser=True
    user.set_password(settings.TEST_USERPASS)
    user.save()


if __name__ == "__main__":
    # local test

    import django
    os.environ['DJANGO_SETTINGS_MODULE'] = 'pylucid_design_demo.settings'
    django.setup()

    from django.core.management import call_command
    # call_command("migrate")
    create_pages()