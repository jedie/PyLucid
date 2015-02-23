# coding: utf-8

"""
    PyLucid v1.x migration to django-cms
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    TODO:
        * Handle permalink in page content!

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import unicode_literals

from pprint import pprint
import traceback

import pygments
from pygments import lexers

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

import cms
from cms.api import create_page, create_title, add_plugin, get_page_draft
from cms.models import Placeholder

from pylucid_migration.markup.converter import markup2html
from pylucid_migration.markup.django_tags import PartTag, PartBlockTag, PartLucidTag
from pylucid_migration.models import PageTree, PageMeta, PageContent


def content2plugins(placeholder,raw_content, markup, language):

    html, splitted_content = markup2html(raw_content, markup)
    # pprint(splitted_content)
    print(",".join([part.kind for part in splitted_content]))

    for part in splitted_content:
        content = part.content
        if isinstance(part, PartLucidTag):
            plugin_name = part.plugin_name
            method_name = part.method_name
            method_kwargs = part.method_kwargs
            content = "TODO: lucidTag: %r %r %r" % (plugin_name, method_name, method_kwargs)
            html += content
            print("\t +++ %s" % content)
            add_plugin(placeholder, "TextPlugin", language, body=content)

        elif isinstance(part, PartBlockTag):
            tag = part.tag
            args = part.args

            print("\tBlockTag %r args: %r" % (tag, args))
            # print("\tBlockTag %r args: %r content: %r" % (tag, args, content))

            if tag == "sourcecode":
                print("\t\t *** create 'CMSPygmentsPlugin' page ")

                content, lexer = part.get_pygments_info()

                add_plugin(placeholder, "CMSPygmentsPlugin", language=language,
                    code_language=lexer.aliases[0],
                    code=content,
                    style="default"
                )
                print("\t\t *** created with %r" % lexer.aliases[0])
            else:
                print("\t *** TODO: BlockTag %r !" % tag)
                # TODO
                content = "TODO: %s" % content
                add_plugin(placeholder, "TextPlugin", language, body=content)

        elif isinstance(part, PartTag):
            print("\tTag content: %r" % content)
            if content == "{% lucidTag SiteMap %}":
                print("\t *** create 'HtmlSitemapPlugin' page ")
                add_plugin(placeholder, "HtmlSitemapPlugin", language)
            else:
                # TODO:
                content = "TODO PartTag: %s" % content
                print("\t *** %s" % content)
                add_plugin(placeholder, "TextPlugin", language, body=content)
        else:
            add_plugin(placeholder, "TextPlugin", language, body=content)

    return html