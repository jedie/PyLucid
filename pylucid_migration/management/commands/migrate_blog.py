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


class Command(BaseCommand):
    help = 'Migrate the PyLucid Blog to djangocms-blog'

    def _split_tags(self, tags):
        tags = tags.lower()
        if "," in tags:
            tags = tags.split(",")
        else:
            tags = tags.split(" ")
        return set([tag.strip() for tag in tags if tag.strip()])

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
        queryset = queryset[453:456] # XXX: only test!
        for content_entry in queryset:
            self.stdout.write("\n")
            self.stdout.write(
                "%s - %s" % (content_entry.url_date, content_entry.slug)
            )
            self.stdout.write(content_entry.headline)

            language = content_entry.language.code

            # # TODO:
            # content = content_entry.content
            # content = markup2html(content, content_entry.markup)
            # # print(content)
            # # continue

            # convert tags
            self.stdout.write("tags: %r" % content_entry.tags)
            tags = self._split_tags(content_entry.tags)
            self.stdout.write("tags: %r" % tags)

            # Use the most common tag as a category:
            categories = [(tag_counter[tag], tag) for tag in tags]
            # print(categories)
            categories.sort(reverse=True)
            try:
                most_common_category = categories[0][1]
            except IndexError:
                most_common_category = "Uncategorized"

            new_post, created = Post.objects.get_or_create(
                author=content_entry.createby,
                date_created=content_entry.createtime,
                date_modified=content_entry.lastupdatetime,
            )

            new_post.set_current_language(language)
            new_post.title = content_entry.headline
            new_post.slug = content_entry.slug

            disable_auto_fields(new_post) # Disable django datetime auto_now and auto_now_add
            new_post.date_created = content_entry.createtime
            new_post.date_modified = content_entry.lastupdatetime

            if content_entry.is_public:
                new_post.publish = True
                new_post.date_published = content_entry.createtime
            new_post.save()

            # add_plugin(new_post.content, 'TextPlugin', language, body=content)

            html = content2plugins(new_post.content, content_entry.content, content_entry.markup, language)
            new_post.abstract = truncatewords_html(html, 20)

            # add tags
            if tags:
                for tag in tags:
                    new_post.tags.add(tag)

            try:
                category = BlogCategory.objects.language(language).get(
                    translations__name=most_common_category
                )
            except BlogCategory.DoesNotExist:
                category = BlogCategory()
                category.set_current_language(language)
                category.name = most_common_category
                category.save()
            new_post.categories.add(category.pk)

            new_post.save()

            self.stdout.write("Blog entry created: %r" % new_post)
            self.stdout.write("pk: %r" % new_post.pk)
            self.stdout.write("title: %r" % new_post.title)
            self.stdout.write("content: %r" % new_post.content)


