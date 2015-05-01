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

from django.db import transaction
from django.contrib.auth.models import User

import cms
from cms.api import create_page, create_title, get_page_draft
from cms.models import Placeholder
from cms.models.permissionmodels import PagePermission,ACCESS_PAGE_AND_DESCENDANTS

from pylucid_migration.management.migrate_base import MigrateBaseCommand, StatusLine
from pylucid_migration.models import PageTree, PageMeta, PageContent
from pylucid_migration.split_content import content2plugins




class Command(MigrateBaseCommand):
    help = 'Migrate PyLucid v1 to v2'

    def _migrate_pagetree(self, options, count, tree, user, site):
        print("\nMigrate pages from site %s" % site.name)
        pages = {}
        with StatusLine(count) as status_line:
            for no, node in enumerate(tree.iter_flat_list(), start=1):
                pagetree = PageTree.objects.get(id=node.id)
                url = pagetree.get_absolute_url()
                status_line.write(no, url)

                self.file_log.debug("%s - %s" % (site.name, url))

                for pagemeta in PageMeta.objects.filter(pagetree=pagetree):
                    try:
                        pagecontent = PageContent.objects.get(pagemeta=pagemeta)
                    except PageContent.DoesNotExist:
                        continue

                    url = pagemeta.get_absolute_url()

                    # TODO: Activate after user/groups migration is implemented:
                    # if pagemeta.permitViewGroup==None and pagetree.permitViewGroup==None:
                    #     login_required=False
                    # else:
                    #     login_required=True

                    if pagetree.id in pages:
                        # Was created before in other language
                        page = pages[pagetree.id]
                        self.file_log.debug("\t * Add in language %r: %s" % (pagemeta.language.code, url))

                        create_title(
                            language=pagemeta.language.code,
                            title=pagemeta.get_title(),
                            page=page,
                            slug=pagetree.slug,
                            meta_description=pagemeta.description,
                        )
                        # page.rescan_placeholders()
                        # page = page.reload()
                    else:
                        self.file_log.debug("\t * Create in language %r: %s" % (pagemeta.language.code, url))
                        if pagetree.parent:
                            # self.file_log.debug("parent: %r" % pagetree.parent.get_absolute_url())
                            parent = pages[pagetree.parent.id]
                        else:
                            parent = None

                        # http://docs.django-cms.org/en/support-3.0.x/reference/api_references.html#cms.api.create_page
                        page = create_page(
                            title=pagemeta.get_title(),
                            menu_title=pagemeta.get_name(),

                            template=cms.constants.TEMPLATE_INHERITANCE_MAGIC,
                            language=pagemeta.language.code,
                            slug=pagetree.slug,
                            # apphook=None, apphook_namespace=None, redirect=None,
                            meta_description=pagemeta.description,
                            created_by='pylucid_migration',
                            parent=parent,
                            # publication_date=None, publication_end_date=None,

                            # Accessable for all users, but don't put a Link to this page into menu/sitemap etc.
                            in_navigation=pagetree.showlinks,

                            # soft_root=False, reverse_id=None,
                            # navigation_extenders=None,
                            published=False,
                            site=site,
                            # login_required=login_required,
                            # limit_visibility_in_menu=VISIBILITY_ALL,
                            # position="last-child", overwrite_url=None, xframe_options=Page.X_FRAME_OPTIONS_INHERIT
                        )

                        # TODO: after user/groups migration is implemented:
                        # pagemeta.permitViewGroup # Limit viewable this page in this language to a user group?
                        # pagetree.permitViewGroup # Limit viewable to a group?

                        # print("XXX", pagetree.permitViewGroup)
                        # print("YYY", pagemeta.permitViewGroup)

                        # view_group = pagetree.permitViewGroup or pagemeta.permitViewGroup
                        # edit_group = pagetree.permitEditGroup # Usergroup how can edit this page.

                        # page_permission = PagePermission(
                        #     page=page,
                        #     user = None,
                        #     group =
                        #     grant_on=ACCESS_PAGE_AND_DESCENDANTS,
                        #     # can_add=
                        #     # can_change=
                        #     # can_delete=
                        #     # can_change_advanced_settings=
                        #     # can_publish=
                        #     # can_change_permissions=
                        #     # can_move_page=
                        #     # can_view=
                        # )
                        # page_permission.save()

                        pages[pagetree.id] = page

                        placeholder = Placeholder.objects.create(slot="content")
                        placeholder.save()
                        page.placeholders.add(placeholder)
                        placeholder.page = page

                    page = get_page_draft(page)

                    content2plugins(options, placeholder, pagecontent.content, pagecontent.markup, pagemeta.language.code)

                    page.publish(pagemeta.language.code)


    def _migrate_pylucid(self, options):
        user = User.objects.all().filter(is_superuser=True)[0]

        for site in self.sites:
            self.file_log.debug("-"*79)
            self.file_log.debug(" *** migrate page content for site: %s ***" % site.name)
            with transaction.atomic():
                count, tree = PageTree.objects.get_tree(site=site)
                self._migrate_pagetree(options, count, tree, user, site)


    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)

        try:
            self._migrate_pylucid(options)
        except Exception:
            traceback.print_exc(file=self.stderr)



