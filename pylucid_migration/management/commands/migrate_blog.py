# coding: utf-8

"""
    PyLucid v1.x blog migration to djangocms-blog
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    #!/bin/bash

    set -x
    rm example_project.db
    cp "fresh.db" example_project.db
    ./manage.py migrate_blog


    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import unicode_literals

import collections

from django.conf import settings
from django.template.defaultfilters import truncatewords_html
from django.db import transaction
from django.utils import translation

from djangocms_blog.cms_app import BlogApp
from djangocms_blog.cms_appconfig import BlogConfig
from djangocms_blog.models import Post, BlogCategory
from djangocms_blog.settings import get_setting as get_blog_settings

from pylucid_migration.management.migrate_base import MigrateBaseCommand, StatusLine
from pylucid_migration.models import BlogEntryContent
from pylucid_migration.markup.converter import markup2html
from pylucid_migration.split_content import content2plugins


def disable_auto_fields(model_instance):
    """
    Disable django datetime auto_now and auto_now_add.
    Otherwise the date can not be set.
    """
    ATTR_NAMES = ("auto_now", "auto_now_add")
    for field in model_instance._meta.local_fields:
        for attr_name in ATTR_NAMES:
            if getattr(field, attr_name, False) == True:
                setattr(field, attr_name, False)


class Command(MigrateBaseCommand):
    help = 'Migrate the PyLucid Blog to djangocms-blog'

    def _split_tags(self, tags):
        tags = tags.lower()
        if "," in tags:
            tags = tags.split(",")
        else:
            tags = tags.split(" ")
        return set([tag.strip() for tag in tags if tag.strip()])

    def _get_tag_counter(self, site):
        all_tags = BlogEntryContent.objects.all().filter(entry__sites=site).values_list("tags", flat=True)
        tag_counter = collections.Counter()
        # print("\t%s" % repr(all_tags))
        for tags in all_tags:
            tags = self._split_tags(tags)
            for tag in tags:
                tag_counter[tag] += 1
        # print("\t%s" % repr(tag_counter))
        return tag_counter

    def _migrate_blog(self, options, site):
        msg = " *** Migrate blog on site %r ***" % site.name
        print("\n%s" % msg)
        self.file_log.debug(msg)
        count = BlogEntryContent.objects.all().filter(entry__sites=site).count()
        self.file_log.debug("\tThere are %i Blog entries on site %r" % (count, site.name))

        tag_counter = self._get_tag_counter(site)

        queryset = BlogEntryContent.objects.all().filter(entry__sites=site).order_by("createtime")
        blog_count=queryset.count()
        print("%i blog entries to migrate." % blog_count)

        if not blog_count:
            print("Skip, because this site has no blog article.")
            return

        blog_namespace = get_blog_settings('AUTO_NAMESPACE')
        app_config, created = BlogConfig.objects.get_or_create(namespace=blog_namespace)
        if created:
            print("App config for %r created." % site.name)
        else:
            print("Use existing %r app config." % site.name)

        with StatusLine(queryset.count()) as status_line:
            for no, content_entry in enumerate(queryset, start=1):

                language = content_entry.language.code
                translation.activate(language)

                msg = "%s /%s/" % (content_entry.url_date, content_entry.slug)
                status_line.write(no, msg)
                self.file_log.debug(msg)

                # # TODO:
                # content = content_entry.content
                # content = markup2html(content, content_entry.markup)
                # # print(content)
                # # continue

                new_post, created = Post.objects.get_or_create(
                    author=content_entry.createby,
                    date_created=content_entry.createtime,
                    date_modified=content_entry.lastupdatetime,
                    app_config=app_config,
                )

                new_post.set_current_language(language, initialize=True)
                new_post.title = content_entry.headline
                new_post.slug = content_entry.slug

                html = content2plugins(options, new_post.content, content_entry.content, content_entry.markup, language)
                new_post.post_text = html
                new_post.abstract = truncatewords_html(html, 20)

                disable_auto_fields(new_post) # Disable django datetime auto_now and auto_now_add
                new_post.date_created = content_entry.createtime
                new_post.date_modified = content_entry.lastupdatetime

                if content_entry.is_public:
                    new_post.publish = True
                    new_post.date_published = content_entry.createtime

                new_post.save()
                new_post.sites.add(site)

                # convert tags
                # self.file_log.debug("\ttags: %r" % content_entry.tags)
                tags = self._split_tags(content_entry.tags)
                # add tags
                if tags:
                    for tag in tags:
                        new_post.tags.add(tag)

                # Use the most common tag as a category:
                categories = [(tag_counter[tag], tag) for tag in tags]
                # print(categories)
                categories.sort(reverse=True)
                try:
                    most_common_category = categories[0][1]
                except IndexError:
                    most_common_category = "Uncategorized"

                try:
                    category = BlogCategory.objects.language(language).get(
                        translations__name=most_common_category
                    )
                except BlogCategory.DoesNotExist:
                    category = BlogCategory(app_config=app_config)
                    category.set_current_language(language, initialize=True)
                    category.name = most_common_category
                    category.save()
                new_post.categories.add(category.pk)

                new_post.save()

                self.file_log.debug("\tBlog entry created: %r" % new_post)

                self.file_log.debug("\t\texists on sites: %r" % ", ".join([s.name for s in new_post.sites.all()]))
                # self.file_log.debug("\t\tpk: %r" % new_post.pk)
                # self.file_log.debug("\t\ttitle: %r" % new_post.title)
                self.file_log.debug("\t\ttags: %r" % new_post.tags.names())
                # self.file_log.debug("\t\tcontent: %r" % new_post.content)

    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)

        BlogApp.setup() # Call "autosetup" explicit

        for site in self.sites:
            with transaction.atomic():
                self.file_log.debug("-"*79)
                self._migrate_blog(options, site)