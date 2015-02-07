# coding: utf-8

"""
    PyLucid v1.x migration to django-cms
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    #!/bin/bash

    set -x
    rm example_project.db
    cp "fresh.db" example_project.db
    ./manage.py migrate pylucid_migration 0001_initial


    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import unicode_literals

from pprint import pprint
import traceback
import sys
from pygments import lexers

from django.db import models, migrations
import pygments

from pylucid_migration.markup.converter import apply_markup
from pylucid_migration.markup.django_tags import PartTag, PartBlockTag



def _migrate_pylucid(apps, schema_editor):
    from cms.api import create_page, create_title, add_plugin, get_page_draft
    import cms
    from cms.models import Placeholder, Title, Page

    #PageTree = apps.get_model(u'pylucid_migration', "PageTree")
    from pylucid_migration.models import PageTree, PageMeta, PageContent

    from django.contrib.auth.models import User
    user = User.objects.all().filter(is_superuser=True)[0]

    tree = PageTree.objects.get_tree()

    pages = {}
    for node in tree.iter_flat_list():
        pagetree = PageTree.objects.get(id=node.id)
        url = pagetree.get_absolute_url()
        print(url)

        for pagemeta in PageMeta.objects.filter(pagetree=pagetree):
            try:
                pagecontent = PageContent.objects.get(pagemeta=pagemeta)
            except PageContent.DoesNotExist:
                continue

            url = pagemeta.get_absolute_url()
            print("\t%s" % url)

            if pagetree.id in pages:
                # Was created before in other language
                page = pages[pagetree.id]
                print("\t * Add in language %r" % pagemeta.language.code)

                create_title(pagemeta.language.code, pagemeta.title, page, slug=pagetree.slug)
                # page.rescan_placeholders()
                # page = page.reload()
            else:
                print("\t * Create in language %r" % pagemeta.language.code)
                if pagetree.parent:
                    # print("parent: %r" % pagetree.parent.get_absolute_url())
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
            # pprint(splitted_content)
            pprint(",".join([part.kind for part in splitted_content]))
            for part in splitted_content:
                content = part.content
                if isinstance(part, PartBlockTag):
                    tag=part.tag
                    args=part.args

                    print("\tBlockTag %r args: %r content: %r" % (tag, args, content))

                    if tag=="sourcecode":
                        print("\t *** create 'CMSPygmentsPlugin' page ")
                        source_type=args.split('"')[1]
                        print("source type: %r" % source_type)
                        content = content.strip()

                        try:
                            lexer = lexers.get_lexer_by_name(source_type.strip("."))
                        except pygments.util.ClassNotFound:
                            try:
                                lexer = lexers.guess_lexer(content)
                            except pygments.util.ClassNotFound:
                                lexer = lexers.get_lexer_by_name("text")

                        add_plugin(placeholder, "CMSPygmentsPlugin", language=pagemeta.language.code,
                            code_language=lexer.aliases[0],
                            code=content,
                            style="default"
                        )
                    else:
                        # TODO
                        content = "TODO: %s" % content
                        add_plugin(placeholder, "TextPlugin", pagemeta.language.code, body=content)

                if isinstance(part, PartTag):
                    print("\tTag content: %r" % content)
                    if content=="{% lucidTag SiteMap %}":
                        print("\t *** create 'HtmlSitemapPlugin' page ")
                        add_plugin(placeholder, "HtmlSitemapPlugin", pagemeta.language.code)
                    else:
                        # TODO
                        content = "TODO: %s" % content
                        add_plugin(placeholder, "TextPlugin", pagemeta.language.code, body=content)
                else:
                    add_plugin(placeholder, "TextPlugin", pagemeta.language.code, body=content)

            page.publish(pagemeta.language.code)




def forwards_func(apps, schema_editor):
    try:
        _migrate_pylucid(apps, schema_editor)
    except Exception:
        traceback.print_exc(file=sys.stderr)


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
        ),
    ]
