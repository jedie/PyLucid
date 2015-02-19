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
import collections

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.template.defaultfilters import truncatewords_html

from cms.api import add_plugin

from djangocms_blog.models import Post, BlogCategory

from pylucid_migration.models import BlogEntryContent
from pylucid_migration.markup.converter import apply_markup


class Command(BaseCommand):
    help = 'Migrate the PyLucid Blog to djangocms-blog'

    def _split_tags(self, tags):
        if "," in tags:
            tags = tags.split(",")
        else:
            tags = tags.split(" ")
        return [tag.strip() for tag in tags if tag.strip()]

    def _get_tag_counter(self):
        all_tags = BlogEntryContent.objects.values_list("tags", flat=True)
        tag_counter = collections.Counter()
        print(all_tags)
        for tags in all_tags:
            tags = self._split_tags(tags)
            for tag in tags:
                tag_counter[tag] += 1
        print(tag_counter)
        return tag_counter

    def handle(self, *args, **options):
        count = BlogEntryContent.objects.count()
        self.stdout.write("There are %i Blog entries." % count)

        tag_counter = self._get_tag_counter()

        for site in Site.objects.all():
            self.stdout.write("\n **** %s ****\n" % site.name)

        queryset = BlogEntryContent.objects.all().order_by("createtime")
        for content_entry in queryset:
            self.stdout.write(
                "%s - %s" % (content_entry.url_date, content_entry.slug)
            )
            self.stdout.write(content_entry.headline)

            self.stdout.write("\n")

            # TODO:
            content = content_entry.content
            content = apply_markup(content, content_entry.markup)

            new_post = Post()
            new_post.author = content_entry.createby
            new_post.set_current_language(content_entry.language.code)
            new_post.title = content_entry.headline
            new_post.slug =content_entry.slug
            new_post.abstract = truncatewords_html(content, 20)
            new_post.date_created = content_entry.createtime

            # TODO: Check is_public !
            new_post.date_published = content_entry.createtime

            new_post.date_modified = content_entry.lastupdatetime
            new_post.save()

            add_plugin(new_post.content, 'TextPlugin', content_entry.language, body=content)

            # add tags
            self.stdout.write("tags: %r" % content_entry.tags)
            tags = self._split_tags(content_entry.tags)
            self.stdout.write("tags: %r" % tags)

            if tags:
                for tag in tags:
                    new_post.tags.add(tag)

            # Use the most common tag as a category:
            categories = [(tag_counter[tag], tag) for tag in tags]
            # print(categories)
            categories.sort()
            most_common_category = categories[-1] or "Uncategorized"

            try:
                category = BlogCategory.objects.language(content_entry.language).get(
                    translations__name=most_common_category
                )
            except BlogCategory.DoesNotExist:
                category = BlogCategory()
                category.set_current_language(content_entry.language.code)
                category.name = most_common_category
                category.save()
            new_post.categories.add(category.pk)

            new_post.save()




