# coding: utf-8

"""
    PyLucid models
    ~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group

# http://code.google.com/p/django-tools/
from django_tools.middlewares import ThreadLocal

from pylucid.shortcuts import failsafe_message

from pylucid_project.pylucid_plugins import update_journal


TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"




class LanguageManager(models.Manager):
    def filter_accessible(self, queryset, user):
        """ filter all pages with can't accessible for the given user """

        if user.is_anonymous():
            # Anonymous user are in no user group
            return queryset.filter(permitViewGroup__isnull=True)

        if user.is_superuser:
            # Superuser can see everything ;)
            return queryset

        # filter pages for not superuser and not anonymous

        user_groups = user.groups.values_list('pk', flat=True)

        if not user_groups:
            # User is in no group
            return queryset.filter(permitViewGroup__isnull=True)

        # Filter out all view group
        return queryset.filter(
            models.Q(permitViewGroup__isnull=True) | models.Q(permitViewGroup__in=user_groups)
        )

    def all_accessible(self, user):
        """ returns all pages that the given user can access. """
        queryset = self.all()
        queryset = self.filter_accessible(queryset, user)
        return queryset

    def get_choices(self):
        """ return a tuple list for e.g. forms.ChoiceField """
        return self.values_list('code', 'description')

    default_lang_entry = None
    def get_default(self):
        if self.default_lang_entry is None:
            lang_code = settings.LANGUAGE_CODE.split("-")[0]
            self.default_lang_entry, created = self.get_or_create(
                code=lang_code, defaults={'description': lang_code}
            )
            if created:
                failsafe_message("Default language entry %r created." % self.default_lang_entry)
        return self.default_lang_entry

    def get_current(self, request=None):
        """ return client Language instance, if not available, use get_default_lang_entry() """
        if request == None:
            request = ThreadLocal.get_current_request()

        if request:
            if hasattr(request, "PYLUCID"):
                return request.PYLUCID.lang_entry

            if hasattr(request, "LANGUAGE_CODE"):
                lang_code = request.LANGUAGE_CODE
                if "-" in lang_code:
                    lang_code = lang_code.split("-", 1)[0]
                try:
                    return self.get(code=lang_code)
                except Language.DoesNotExist:
                    if settings.PYLUCID.I18N_DEBUG:
                        msg = (
                            'Favored language "%s" does not exist -> use default lang from system preferences'
                        ) % request.LANGUAGE_CODE
                        failsafe_message(msg)

        return self.get_default()


class Language(models.Model):
    objects = LanguageManager()

    code = models.CharField(unique=True, max_length=5)
    description = models.CharField(max_length=150, help_text="Description of the Language")

    permitViewGroup = models.ForeignKey(Group, related_name="%(class)s_permitViewGroup",
        help_text="Limit viewable to a group for a complete language section?",
        null=True, blank=True,
    )

    def __unicode__(self):
        return u"Language %s - %s" % (self.code, self.description)

    class Meta:
        app_label = 'pylucid'
        ordering = ("code",)
