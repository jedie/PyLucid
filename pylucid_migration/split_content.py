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

from cms.api import add_plugin

from pylucid_migration.markup.converter import markup2html
from pylucid_migration.markup.django_tags import PartText, PartTag, PartBlockTag, PartLucidTag


def _add_todo(placeholder, language, content):
    print("\t +++ Add TODO Plugin for: %r" % content)
    add_plugin(placeholder, "ToDoPlugin", language, code=content)


def content2plugins(placeholder, raw_content, markup, language):
    html, splitted_content = markup2html(raw_content, markup)
    # pprint(splitted_content)
    # print(",".join([part.kind for part in splitted_content]))

    for part in splitted_content:
        content = part.content
        if isinstance(part, PartLucidTag):
            # plugin_name = part.plugin_name
            # method_name = part.method_name
            # method_kwargs = part.method_kwargs
            # content = "TODO: lucidTag: %r %r %r" % (plugin_name, method_name, method_kwargs)
            # html += content
            _add_todo(placeholder, language, content)

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
                _add_todo(placeholder, language, content)

        elif isinstance(part, PartTag):
            print("\tTag content: %r" % content)
            if content == "{% lucidTag SiteMap %}":
                print("\t *** create 'HtmlSitemapPlugin' page ")
                add_plugin(placeholder, "HtmlSitemapPlugin", language)
            else:
                _add_todo(placeholder, language, content)
        elif isinstance(part, PartText):
            add_plugin(placeholder, "TextPlugin", language, body=content)
        else:
            raise NotImplementedError(repr(part))

    return html