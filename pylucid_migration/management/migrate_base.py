# coding: utf-8

"""
    Create pages for djangocms-blog
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from optparse import make_option

from django.db import transaction
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.utils.translation import activate
from django.conf import settings
from django.core.management.base import BaseCommand

from pylucid_migration.models import DjangoSite

class MigrateBaseCommand(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--inline_script',
            action='store_true',
            dest='inline_script',
            default=False,
            help='Move inline javascript into "html" markup entry.'),
    )

    def _migrate_sites(self):
        self.stdout.write("Migrate Sites:")
        for site_old in DjangoSite.objects.all():
            try:
                site_new = Site.objects.get(pk=site_old.pk)
            except Site.DoesNotExist:
                site_new = Site.objects.create(
                    pk=site_old.pk,
                    domain=site_old.domain,
                    name=site_old.name,
                )
                self.stdout.write("\tNew site %r with ID %i created." % (site_new.name, site_new.id))
            else:
                self.stdout.write("\tSite %r with ID %i exists, ok." % (site_new.name, site_new.id))
