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
from cms import constants
from cms.api import create_page, create_title, get_page_draft, publish_page
from cms.models import Placeholder
from cms.models.permissionmodels import PagePermission, ACCESS_PAGE_AND_DESCENDANTS

from pylucid_migration.management.migrate_base import MigrateBaseCommand, StatusLine
from pylucid_migration.models import PageTree, PageMeta, PageContent, PageProxyModel, PagePatchModel
from pylucid_migration.split_content import content2plugins


class PageMetaPatcher(object):
    def __init__(self, created_by, creation_date, changed_by, changed_date):
        self.created_by = created_by
        self.creation_date = creation_date
        self.changed_by = changed_by
        self.changed_date = changed_date

    def patch(self, page):
        # print("Patch ID: %i - %s" % (page.pk, page))
        patch_page = PagePatchModel.objects.get(pk=page.pk)
        patch_page.created_by = self.created_by
        patch_page.creation_date = self.creation_date
        patch_page.changed_by = self.changed_by
        patch_page.changed_date = self.changed_date
        patch_page.save()
        # print(patch_page.created_by, patch_page.creation_date, patch_page.changed_by, patch_page.changed_date)


class Command(MigrateBaseCommand):
    help = 'Migrate PyLucid v1 to v2'

    _PAGES = {}

    def _migrate_page(self, options, site, pagetree, pagemeta, pagecontent):
        url = pagemeta.get_absolute_url()
        created_py = self.USER_MAP[pagemeta.createby.pk]
        changed_by = self.USER_MAP[pagemeta.lastupdateby.pk]

        if pagemeta.permitViewGroup == None and pagetree.permitViewGroup == None:
            login_required = False
            visibility = constants.VISIBILITY_ALL
        else:
            login_required = True
            visibility = constants.VISIBILITY_USERS

        if pagetree.id in self._PAGES:
            # Was created before in other language
            page = self._PAGES[pagetree.id]
            self.file_log.debug("\t * Add in language %r: %s" % (pagemeta.language.code, url))

            create_title(
                language=pagemeta.language.code,
                title=pagemeta.get_title(),
                menu_title=pagemeta.name,
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
                parent = self._PAGES[pagetree.parent.id]
            else:
                parent = None

            # http://docs.django-cms.org/en/latest/reference/api_references.html#cms.api.create_page
            page = create_page(
                title=pagemeta.get_title(),
                menu_title=pagemeta.get_name(),

                template=cms.constants.TEMPLATE_INHERITANCE_MAGIC,
                language=pagemeta.language.code,
                slug=pagetree.slug,
                # apphook=None, apphook_namespace=None, redirect=None,
                meta_description=pagemeta.description,
                created_by=created_py,
                parent=parent,
                # publication_date=None, publication_end_date=None,

                # Accessable for all users, but don't put a Link to this page into menu/sitemap etc.
                in_navigation=pagetree.showlinks,

                # soft_root=False, reverse_id=None,
                # navigation_extenders=None,
                published=False,
                site=site,

                login_required=login_required,
                limit_visibility_in_menu=visibility,

                # position="last-child", overwrite_url=None, xframe_options=Page.X_FRAME_OPTIONS_INHERIT
            )

            self._PAGES[pagetree.id] = page

        # pagemeta.permitViewGroup # Limit viewable this page in this language to a user group?
        # pagetree.permitViewGroup # Limit viewable to a group?
        view_group = pagetree.permitViewGroup or pagemeta.permitViewGroup
        edit_group = pagetree.permitEditGroup  # Usergroup how can edit this page.
        # print("\nview:", view_group, "edit:", edit_group)

        if view_group and edit_group and view_group == edit_group:
            page_permission = PagePermission(
                page=page,
                user=None,
                group=edit_group,
                grant_on=ACCESS_PAGE_AND_DESCENDANTS,
                can_add=True,
                can_change=True,
                can_delete=True,
                can_change_advanced_settings=True,
                can_publish=True,
                can_change_permissions=True,
                can_move_page=True,
                can_view=True,
            )
            page_permission.save()
        else:
            if view_group:
                page_permission = PagePermission(
                    page=page,
                    user=None,
                    group=view_group,
                    grant_on=ACCESS_PAGE_AND_DESCENDANTS,
                    can_add=False,
                    can_change=False,
                    can_delete=False,
                    can_change_advanced_settings=False,
                    can_publish=False,
                    can_change_permissions=False,
                    can_move_page=False,
                    can_view=True,
                )
                page_permission.save()

            if edit_group:
                page_permission = PagePermission(
                    page=page,
                    user=None,
                    group=view_group,
                    grant_on=ACCESS_PAGE_AND_DESCENDANTS,
                    can_add=True,
                    can_change=True,
                    can_delete=True,
                    can_change_advanced_settings=True,
                    can_publish=True,
                    can_change_permissions=True,
                    can_move_page=True,
                    can_view=True,
                )
                page_permission.save()

        placeholder = page.placeholders.filter(slot="content")[0]
        content2plugins(options, placeholder, pagecontent.content, pagecontent.markup,
                        pagemeta.language.code)

        page.publish(pagemeta.language.code)

        # using api.publish_page() will result in django.db.utils.IntegrityError:
        #       UNIQUE constraint failed: cms_page.publisher_public_id
        # published_page = publish_page(page, user=changed_by, language=pagemeta.language.code)

        page_meta_patcher = PageMetaPatcher(
            created_by=created_py.username,
            creation_date=pagemeta.createtime,
            changed_by=changed_by.username,
            changed_date=pagemeta.lastupdatetime,
        )

        # print("\npatch draft version")
        draft_page = page.get_draft_object()
        page_meta_patcher.patch(draft_page)  # patch the draft version

        # print("patch the published version")
        published_page = page.get_public_object()
        page_meta_patcher.patch(published_page)  # patch the published version
        # print("patch done.")

    def _migrate_pagetree(self, options, count, tree, user, site):
        print("\nMigrate pages from site %s" % site.name)
        self._PAGES = {}
        with StatusLine(count) as status_line: # TODO: update status with pagemeta (include all translations)
            for no, node in enumerate(tree.iter_flat_list(), start=1):
                pagetree = PageTree.objects.get(id=node.id)
                url = pagetree.get_absolute_url()
                status_line.write(no, url) # TODO: update status with pagemeta (include all translations)

                self.file_log.debug("%s - %s" % (site.name, url))

                for pagemeta in PageMeta.objects.filter(pagetree=pagetree):
                    try:
                        pagecontent = PageContent.objects.get(pagemeta=pagemeta)
                    except PageContent.DoesNotExist:
                        continue

                    self._migrate_page(options, site, pagetree, pagemeta, pagecontent)

                # if no>8:
                #     break

    def _migrate_pylucid(self, options):
        user = User.objects.all().filter(is_superuser=True)[0]

        for site in self.sites:
            self.file_log.debug("-" * 79)
            self.file_log.debug(" *** migrate page content for site: %s ***" % site.name)
            with transaction.atomic():
                count, tree = PageTree.objects.get_tree(site=site)
                self._migrate_pagetree(options, count, tree, user, site)

    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
        self._migrate_pylucid(options)
