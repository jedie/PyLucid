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



from django.core.management.base import BaseCommand, CommandError


from pylucid_migration.models import BlogEntryContent




class Command(BaseCommand):
    help = 'Migrate the PyLucid Blog to djangocms-blog'

    def handle(self, *args, **options):
        count = BlogEntryContent.objects.count()
        self.stdout.write("There are %i Blog entries." % count)

        queryset = BlogEntryContent.objects.all().order_by("createtime")
        for content_entry in queryset:
            self.stdout.write(
                "%s - %s" % (content_entry.url_date, content_entry.slug)
            )
            self.stdout.write(content_entry.headline)
            self.stdout.write("\n")




