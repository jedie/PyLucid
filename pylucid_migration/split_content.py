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

import logging

from cms.api import add_plugin

from cmsplugin_filer_video.cms_plugins import FilerVideoPlugin
from cmsplugin_pygments.cms_plugins import CMSPygmentsPlugin

from pylucid_migration.markup.converter import markup2html
from pylucid_migration.markup.django_tags import PartText, PartDjangoComment, PartTag, PartBlockTag, PartLucidTag
from pylucid_migration.markup.utils import TYPE_SCRIPT, iter_html_and_script


LOG=logging.getLogger(name="PyLucidMigration")


def _add_todo(placeholder, language, content):
    LOG.debug("\t +++ Add TODO Plugin for: %r" % content)
    add_plugin(placeholder, "ToDoPlugin", language, code=content)


def content2plugins(options, placeholder, raw_content, markup, language):
    html, splitted_content = markup2html(raw_content, markup)
    # pLOG.debug(splitted_content)
    # LOG.debug(",".join([part.kind for part in splitted_content]))

    for part in splitted_content:
        content = part.content
        if isinstance(part, PartDjangoComment):
            _add_todo(placeholder, language, content)
        elif isinstance(part, (PartLucidTag, PartDjangoComment)):
            plugin_name = part.plugin_name
            method_name = part.method_name
            method_kwargs = part.method_kwargs
            # LOG.debug(" *** TODO: lucidTag: %r %r %r" % (plugin_name, method_name, method_kwargs))
            # html += content
            #
            if plugin_name=="generic" and method_name=="youtube":
                LOG.debug("\t\t *** Add 'FilerVideoPlugin': %s" % repr(method_kwargs))
                add_plugin(placeholder, FilerVideoPlugin, language=language,
                    movie_url = "http://www.youtube.com/watch?v=%s" % method_kwargs["id"],
                    width = method_kwargs.get("width", 768),
                    height = method_kwargs.get("height", 432),
                )
            else:
                _add_todo(placeholder, language, content)

        elif isinstance(part, PartBlockTag):
            tag = part.tag
            args = part.args

            LOG.debug("\tBlockTag %r args: %r" % (tag, args))
            # LOG.debug("\tBlockTag %r args: %r content: %r" % (tag, args, content))

            if tag == "sourcecode":
                LOG.debug("\t\t *** create 'CMSPygmentsPlugin' page ")

                content, lexer = part.get_pygments_info()

                add_plugin(placeholder, CMSPygmentsPlugin, language=language,
                    code_language=lexer.aliases[0],
                    code=content,
                    style="default"
                )
                LOG.debug("\t\t *** created with %r" % lexer.aliases[0])
            else:
                _add_todo(placeholder, language, content)

        elif isinstance(part, PartTag):
            LOG.debug("\tTag content: %r" % content)
            if content == "{% lucidTag SiteMap %}":
                LOG.debug("\t *** create 'HtmlSitemapPlugin' page ")
                add_plugin(placeholder, "HtmlSitemapPlugin", language)
            # elif content == "{{ page_title }}" or content.startswith("{{ page_title|"):
                #{% page_attribute page_title %}

            else:
                _add_todo(placeholder, language, content)
        elif isinstance(part, PartText):

            if not options["inline_script"]:
                add_plugin(placeholder, "TextPlugin", language, body=content)
            else:
                # Extract JavaScript into MarkupPlugin
                for kind, content in iter_html_and_script(content):
                    if kind == TYPE_SCRIPT:
                        LOG.debug("\t *** create 'MarkupPlugin' html: %r" % content)
                        add_plugin(placeholder, "MarkupPlugin", language, body=content, markup="html")
                    else:
                        add_plugin(placeholder, "TextPlugin", language, body=content)

        else:
            raise NotImplementedError(repr(part))

    return html