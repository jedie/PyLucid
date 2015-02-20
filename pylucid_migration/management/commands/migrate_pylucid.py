# coding: utf-8

"""
    PyLucid v1.x migration to django-cms
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    #!/bin/bash

    set -x
    rm example_project.db
    cp "fresh.db" example_project.db
    ./manage.py migrate_pylucid


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

from pylucid_migration.markup.converter import apply_markup
from pylucid_migration.markup.django_tags import PartTag, PartBlockTag, PartLucidTag
from pylucid_migration.models import PageTree, PageMeta, PageContent


class Command(BaseCommand):
    help = 'Migrate PyLucid v1 to v2'

    def _migrate_pylucid(self):
        user = User.objects.all().filter(is_superuser=True)[0]

        tree = PageTree.objects.get_tree()

        pages = {}
        for node in tree.iter_flat_list():
            pagetree = PageTree.objects.get(id=node.id)
            url = pagetree.get_absolute_url()
            self.stdout.write(url)

            for pagemeta in PageMeta.objects.filter(pagetree=pagetree):
                try:
                    pagecontent = PageContent.objects.get(pagemeta=pagemeta)
                except PageContent.DoesNotExist:
                    continue

                url = pagemeta.get_absolute_url()
                self.stdout.write("\t%s" % url)

                if pagetree.id in pages:
                    # Was created before in other language
                    page = pages[pagetree.id]
                    self.stdout.write("\t * Add in language %r" % pagemeta.language.code)

                    create_title(pagemeta.language.code, pagemeta.title, page, slug=pagetree.slug)
                    # page.rescan_placeholders()
                    # page = page.reload()
                else:
                    self.stdout.write("\t * Create in language %r" % pagemeta.language.code)
                    if pagetree.parent:
                        # self.stdout.write("parent: %r" % pagetree.parent.get_absolute_url())
                        parent = pages[pagetree.parent.id]
                    else:
                        parent = None

                    # http://docs.django-cms.org/en/support-3.0.x/reference/api_references.html#cms.api.create_page
                    page = create_page(
                        title=pagemeta.title,
                        menu_title=pagemeta.name,

                        template=cms.constants.TEMPLATE_INHERITANCE_MAGIC,
                        language=pagemeta.language.code,
                        slug=pagetree.slug,
                        # apphook=None, apphook_namespace=None, redirect=None,
                        meta_description=pagemeta.description,
                        created_by='pylucid_migration',
                        parent=parent,
                        # publication_date=None, publication_end_date=None,
                        in_navigation=pagetree.showlinks,
                        # soft_root=False, reverse_id=None,
                        # navigation_extenders=None,
                        published=False,
                        site=pagetree.site,
                        # login_required=False, limit_visibility_in_menu=VISIBILITY_ALL,
                        # position="last-child", overwrite_url=None, xframe_options=Page.X_FRAME_OPTIONS_INHERIT
                    )
                    pages[pagetree.id] = page

                    placeholder = Placeholder.objects.create(slot="content")
                    placeholder.save()
                    page.placeholders.add(placeholder)
                    placeholder.page = page

                page = get_page_draft(page)

                raw_content = pagecontent.content
                markup = pagecontent.markup

                splitted_content = apply_markup(raw_content, markup)
                # pself.stdout.write(splitted_content)
                self.stdout.write(",".join([part.kind for part in splitted_content]))
                for part in splitted_content:
                    content = part.content
                    if isinstance(part, PartLucidTag):
                        plugin_name = part.plugin_name
                        method_name = part.method_name
                        method_kwargs = part.method_kwargs
                        content = "TODO: lucidTag: %r %r %r" % (plugin_name, method_name, method_kwargs)
                        self.stdout.write("\t +++ %s" % content)
                        add_plugin(placeholder, "TextPlugin", pagemeta.language.code, body=content)

                    elif isinstance(part, PartBlockTag):
                        tag = part.tag
                        args = part.args

                        self.stdout.write("\tBlockTag %r args: %r" % (tag, args))
                        # self.stdout.write("\tBlockTag %r args: %r content: %r" % (tag, args, content))

                        if tag == "sourcecode":
                            self.stdout.write("\t\t *** create 'CMSPygmentsPlugin' page ")

                            content, lexer = part.get_pygments_info()

                            add_plugin(placeholder, "CMSPygmentsPlugin", language=pagemeta.language.code,
                                code_language=lexer.aliases[0],
                                code=content,
                                style="default"
                            )
                            self.stdout.write("\t\t *** created with %r" % lexer.aliases[0])
                        else:
                            self.stdout.write("\t *** TODO: BlockTag %r !" % tag)
                            # TODO
                            content = "TODO: %s" % content
                            add_plugin(placeholder, "TextPlugin", pagemeta.language.code, body=content)

                    elif isinstance(part, PartTag):
                        self.stdout.write("\tTag content: %r" % content)
                        if content == "{% lucidTag SiteMap %}":
                            self.stdout.write("\t *** create 'HtmlSitemapPlugin' page ")
                            add_plugin(placeholder, "HtmlSitemapPlugin", pagemeta.language.code)
                        else:
                            # TODO:
                            content = "TODO PartTag: %s" % content
                            self.stdout.write("\t *** %s" % content)
                            add_plugin(placeholder, "TextPlugin", pagemeta.language.code, body=content)
                    else:
                        add_plugin(placeholder, "TextPlugin", pagemeta.language.code, body=content)

                page.publish(pagemeta.language.code)


    def handle(self, *args, **options):
        try:
            self._migrate_pylucid()
        except Exception:
            traceback.print_exc(file=self.stderr)



