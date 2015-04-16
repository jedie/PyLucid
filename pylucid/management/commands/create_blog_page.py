# coding: utf-8

"""
    Create pages for djangocms-blog
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from optparse import make_option, OptionValueError
import sys

from django.db import transaction
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.utils.translation import activate
from django.conf import settings
from django.core.management.base import BaseCommand
from cms.models import Page, Title, Placeholder, CMSPlugin
from cms.api import create_page, create_title, add_plugin
from cms.utils.i18n import get_language_list, get_default_language


PLUGIN_TYPES = ("BlogArchivePlugin", "BlogAuthorPostsPlugin", "BlogCategoryPlugin", "BlogTagsPlugin")
BLOG_APP_HOOK = "BlogApp"
APP_NAMESPACE = "djangocms_blog"

BLOG_TEMPLATE = "pylucid/bootstrap/sidebar_left.html"
PLACEHOLDER_SLOT = "sidebar" # from 'BLOG_TEMPLATE' template!


def check_template(option, opt, value, parser):
    if parser.values.template not in [tpl[0] for tpl in settings.TEMPLATES]:
        raise OptionValueError("--template %r not exists in settings.TEMPLATES!")


class Command(BaseCommand):
    help = 'Create djangocms-blog page'

    option_list = BaseCommand.option_list + (
        make_option('--delete',
            action='store_true',
            dest='delete',
            default=False,
            help='Delete blog page instead of create it'
        ),
        make_option("--template",
            dest="template", type="string", action="callback",
            default=BLOG_TEMPLATE,
            callback=check_template
        ),
    )

    def _delete_blog(self):
        queryset = Page.objects.filter(application_namespace=APP_NAMESPACE, site=self.site)
        self.stdout.write("Delete %s blog page entries" % queryset.count())
        queryset.delete()

    def _create_blog(self, options):
        default_language = get_default_language()
        languages = get_language_list()

        activate(default_language)

        try:
            blog_page = Page.objects.get(
                application_namespace=APP_NAMESPACE,
                publisher_is_draft=True,
                site=self.site,
            )
        except Page.DoesNotExist:
            self.stdout.write("Create new blog AppHook page.")

            blog_page = create_page(
                title=_("blog"),
                template=options["template"],
                language=settings.LANGUAGE_CODE,
                apphook=BLOG_APP_HOOK,
                apphook_namespace=APP_NAMESPACE,
                in_navigation=True,
            )
        else:
            self.stdout.write("Use existing blog AppHook page.")

        placeholder, created = Placeholder.objects.get_or_create(slot=PLACEHOLDER_SLOT)
        if created:
            self.stdout.write("New placeholder for blog page created.")
            placeholder.save()
        else:
            self.stdout.write("Use existing placeholder for blog page.")

        for language in languages:
            activate(language)

            if language != default_language:
                if Title.objects.filter(language=language, page=blog_page).exists():
                    self.stdout.write("Use existing title in %r" % language)
                else:
                    self.stdout.write("Create title in %r" % language)
                    create_title(language=language, title=_("blog"), page=blog_page)

            for plugin_type in PLUGIN_TYPES:
                queryset = CMSPlugin.objects.filter(
                    placeholder=placeholder,
                    plugin_type=plugin_type,
                    language=language
                )
                if queryset.exists():
                    self.stdout.write("Use existing plugin %r in %r" % (plugin_type, language))
                else:
                    self.stdout.write("Create plugin %r in %r" % (plugin_type, language))
                    add_plugin(placeholder, plugin_type, language=language)

            # self.stdout.write("publish placeholder in language: %r" % language)
            # placeholder.publish(request=None, language=language, force=True)

            self.stdout.write("publish blog page in language: %r" % language)
            blog_page.publish(language)

    def handle(self, *args, **options):
        try:
            self.site = Site.objects.get_current()
        except Site.DoesNotExist:
            self.stderr.write("Error: SITE_ID %i doesn't exists!" % settings.SITE_ID)
            self.stderr.write("Please check SITE_ID in your settings.py!")
            sys.exit(-1)

        with transaction.atomic():
            if options['delete']:
                self._delete_blog()
            else:
                self._create_blog(options)