# coding: utf-8

"""
    Create pages for djangocms-blog
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.utils.translation import ugettext as _
from django.utils.translation import activate
from django.conf import settings

from django.core.management.base import BaseCommand

from cms.models import Placeholder, StaticPlaceholder
from cms.api import create_page, create_title, add_plugin
from cms.constants import TEMPLATE_INHERITANCE_MAGIC

from cms.utils.i18n import get_language_list, get_default_language


# The name from pylucid/templates/djangocms_blog/base.html
STATIC_PLACEHOLDER_BLOG = "static_placeholder_blog"


class Command(BaseCommand):
    help = 'Create djangocms-blog page'

    def handle(self, *args, **options):
        default_language= get_default_language()
        languages = get_language_list()

        activate(default_language)

        blog_page = create_page(
            title=_("blog"),
            template = TEMPLATE_INHERITANCE_MAGIC,
            language=settings.LANGUAGE_CODE,
            apphook="BlogApp",
            apphook_namespace="djangocms_blog",
            in_navigation=True,
        )

        static_placeholder = StaticPlaceholder.objects.create(
            name=STATIC_PLACEHOLDER_BLOG, code=STATIC_PLACEHOLDER_BLOG
        )
        static_placeholder.save()

        for language in languages:
            self.stdout.write("Create blog pages in languages: %r" % language)
            activate(language)

            if language != default_language:
                create_title(language=language, title=_("blog"), page=blog_page)

            add_plugin(static_placeholder.draft, "BlogArchivePlugin", language=language)
            add_plugin(static_placeholder.draft, "BlogAuthorPostsPlugin", language=language)
            add_plugin(static_placeholder.draft, "BlogCategoryPlugin", language=language)
            add_plugin(static_placeholder.draft, "BlogTagsPlugin", language=language)

            static_placeholder.publish(request=None, language=language, force=True)
            blog_page.publish(language)
