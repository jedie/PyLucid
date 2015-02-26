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

import traceback

from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

import cms
from cms.api import create_page, create_title, get_page_draft
from cms.models import Placeholder

from pylucid_migration.management.migrate_base import MigrateBaseCommand
from pylucid_migration.models import PageTree, PageMeta, PageContent
from pylucid_migration.split_content import content2plugins


class Command(MigrateBaseCommand):
    help = 'Migrate PyLucid v1 to v2'


    def _migrate_pylucid(self, options):
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

                    create_title(
                        language=pagemeta.language.code,
                        title=pagemeta.title,
                        page=page,
                        slug=pagetree.slug,
                        meta_description=pagemeta.description,
                    )
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

                content2plugins(options, placeholder, pagecontent.content, pagecontent.markup, pagemeta.language.code)

                page.publish(pagemeta.language.code)


    def handle(self, *args, **options):
        try:
            self._migrate_sites()
            self._migrate_pylucid(options)
        except Exception:
            traceback.print_exc(file=self.stderr)



