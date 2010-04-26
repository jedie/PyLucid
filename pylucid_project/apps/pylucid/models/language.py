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
from django.core.exceptions import ValidationError
from django.utils.translation.trans_real import parse_accept_lang_header

# http://code.google.com/p/django-tools/
from django_tools.middlewares import ThreadLocal
from django_tools.fields import LanguageCodeField

from pylucid_project.apps.pylucid.shortcuts import failsafe_message
from pylucid_project.apps.pylucid.models.base_models import UpdateInfoBaseModel, AutoSiteM2M

from pylucid_project.pylucid_plugins import update_journal


supported_languages = dict(settings.LANGUAGES)

TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"


ACCESSIBLE_LANG_CACHE = {}



class LanguageManager(models.Manager):
    def filter_accessible(self, queryset, user):
        """ filter all languages with can't accessible for the given user """

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
        """ returns a QuerySet of all languages that the given user can access. """
        queryset = self.model.on_site.all()
        queryset = self.filter_accessible(queryset, user)
        return queryset

    def get_cached_languages(self, user):
        """ returns a cached *list* of all languages that the given user can access. """
        cache_key = user
        if cache_key not in ACCESSIBLE_LANG_CACHE:
            languages = self.all_accessible(user)
#            if settings.PYLUCID.I18N_DEBUG:
#                failsafe_message("all accessible languages from db: %r" % languages)
            ACCESSIBLE_LANG_CACHE[cache_key] = list(languages)
#        elif settings.PYLUCID.I18N_DEBUG:
#                failsafe_message("all accessible languages from cache: %r" % ACCESSIBLE_LANG_CACHE[cache_key])

        return ACCESSIBLE_LANG_CACHE[cache_key][:]

    def get_choices(self):
        """ return a tuple list for e.g. forms.ChoiceField """
        return self.values_list('code', 'description')

    default_lang_entry = None
    def get_or_create_default(self, request):
        """
        return Language instance with code from settings.LANGUAGE_CODE
        Create if not exist.
        """
        if self.default_lang_entry is None:
            language_code = settings.LANGUAGE_CODE

            self.default_lang_entry = self.get_from_code(request, language_code)
            if self.default_lang_entry is None:
                failsafe_message("Default language entry not in language list?")
                self.default_lang_entry, created = self.get_or_create(
                    code=language_code, defaults={'description': language_code}
                )
                if created:
                    failsafe_message("Default language entry %r created." % self.default_lang_entry)
        return self.default_lang_entry

    def _get_default_language(self):
        """
        return Languange instance with code from settings.LANGUAGE_CODE
        Should normaly not used! Use request.PYLUCID.default_language !
        e.g. needed in unittest
        """
        if self.default_lang_entry is None:
            language_code = settings.LANGUAGE_CODE
            self.default_lang_entry = self.model.on_site.get(code=language_code)
        return self.default_lang_entry

    def _get_language_codes(self, request):
        """
        Create a language code list.
         - use all client accepted languages
         - add current used language and system default language        
        """
        current_lang_code = getattr(request, "LANGUAGE_CODE", None)
        default_lang_code = settings.LANGUAGE_CODE

        accept_lang_codes = []
        unsupported_lang_codes = []
        fallback_lang_codes = []

        accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
#        if settings.PYLUCID.I18N_DEBUG:
#            request.page_msg.info("HTTP_ACCEPT_LANGUAGE: %r" % accept)

        if not accept:
            if current_lang_code:
                accept_lang_codes = [current_lang_code, default_lang_code]
            else:
                accept_lang_codes = [default_lang_code]

            return accept_lang_codes, [], []

        accept_lang_headers = parse_accept_lang_header(accept)
#        print "accept_lang_headers:", accept_lang_headers
        for accept_lang, unused in accept_lang_headers:
            if "-" in accept_lang:
                # remember the first part for later adding as a fallback language
                fallback_lang = accept_lang.split("-", 1)[0]
                if fallback_lang in supported_languages and fallback_lang not in fallback_lang_codes:
                    fallback_lang_codes.append(fallback_lang)

            if accept_lang not in supported_languages:
                unsupported_lang_codes.append(accept_lang)
                continue

            if accept_lang not in accept_lang_codes:
                accept_lang_codes.append(accept_lang)

        if current_lang_code:
            # insert/move current language at the beginning
            if not accept_lang_codes:
                accept_lang_codes = [current_lang_code]
            elif accept_lang_codes[0] != current_lang_code:
                if current_lang_code in accept_lang_codes:
                    pos = accept_lang_codes.index(current_lang_code)
                    del(accept_lang_codes[pos])

                accept_lang_codes.insert(0, current_lang_code)

        # append fallback languages
        for fallback_lang in fallback_lang_codes:
            if fallback_lang not in accept_lang_codes:
                accept_lang_codes.append(fallback_lang)

        # append default language at the end
        if default_lang_code not in accept_lang_codes:
            accept_lang_codes.append(default_lang_code)

        return accept_lang_codes, unsupported_lang_codes, fallback_lang_codes

    def get_languages(self, request):
        """
        Create a list of all languages sorted by client accept language priority.
        
        added to request.PYLUCID.languages
        
        Cache key: The language entry can have a permitViewGroup,
            so we must use different caches for different users.
        """
        if hasattr(request, "PYLUCID") and hasattr(request.PYLUCID, "languages"):
            if settings.PYLUCID.I18N_DEBUG:
                request.page_msg.info(
                    "return request.PYLUCID.languages: %r" % request.PYLUCID.languages
                )
            return request.PYLUCID.languages

        user = request.user
        languages = self.get_cached_languages(user)

        if settings.PYLUCID.I18N_DEBUG:
            failsafe_message("all accessible languages: %r" % languages)

        accept_lang_codes, unsupported_lang_codes, fallback_lang_codes = self._get_language_codes(request)

        if settings.PYLUCID.I18N_DEBUG:
            request.page_msg.info("accept_lang_codes: %r" % accept_lang_codes)
            request.page_msg.info("unsupported_lang_codes: %r" % unsupported_lang_codes)
            request.page_msg.info("fallback_lang_codes: %r" % fallback_lang_codes)

        # XXX: Test QuerySet order
#            language_codes.sort()
#            language_codes.sort(reverse=True)

        # sort the language in the same order than language_codes list was.
        # XXX: It there a better way to do this?
        language_list = []
        for language_code in accept_lang_codes:
            for index, language in enumerate(languages):
                if language.code.lower() == language_code.lower():
                    if language not in language_list:
                        language_list.append(language)
                    del(languages[index])
                    break

        if languages:
            # The Client has not all existing languages in his HTTP_ACCEPT_LANGUAGE
            # Append the rest
            if settings.PYLUCID.I18N_DEBUG:
                request.page_msg.info(
                    "client not accepted languages to append: %s" % ", ".join([l.code for l in languages])
                )
            language_list += languages

        if settings.PYLUCID.I18N_DEBUG:
            request.page_msg.info("language_list: %s" % ", ".join([l.code for l in language_list]))

        return language_list

    def get_from_code(self, request, language_code):
        language_list = self.get_languages(request)
        for language in language_list:
            if language.code.lower() == language_code.lower():
                return language

    def get_current(self, request=None):
        """ return client Language instance, if not available, use get_default_lang_entry() """
        if request == None:
            request = ThreadLocal.get_current_request()

        if request == None:
            # no request available, e.g. loading fixtures
            return self._get_default_language()

        language_list = self.get_languages(request)
        return language_list[0]

#        if request:
#            if hasattr(request, "PYLUCID"):
#                return request.PYLUCID.current_language
#
#            if hasattr(request, "LANGUAGE_CODE"):
#                lang_code = request.LANGUAGE_CODE
#                if "-" in lang_code:
#                    lang_code = lang_code.split("-", 1)[0]
#                try:
#                    return self.get(code=lang_code)
#                except Language.DoesNotExist:
#                    if settings.PYLUCID.I18N_DEBUG:
#                        msg = (
#                            'Favored language "%s" does not exist -> use default lang from system preferences'
#                        ) % request.LANGUAGE_CODE
#                        failsafe_message(msg)
#
#        return self.get_or_create_default(request)




class Language(AutoSiteM2M, UpdateInfoBaseModel):
    """
    inherited attributes from AutoSiteM2M:
        sites   -> ManyToManyField to Site
        on_site -> sites.managers.CurrentSiteManager instance
        
    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    objects = LanguageManager()

    code = LanguageCodeField(unique=True, max_length=10)
    description = models.CharField(max_length=150, blank=True,
        help_text="Description of the Language (filled automaticly)"
    )

    permitViewGroup = models.ForeignKey(Group, related_name="%(class)s_permitViewGroup",
        help_text="Limit viewable to a group for a complete language section?",
        null=True, blank=True,
    )

    def clean_fields(self, exclude):
        message_dict = {}

        if "code" not in exclude and self.code not in supported_languages:
            message_dict["code"] = (
                "Language is not in settings.LANGUAGES!",
                "Supported languages are: %s" % ",".join(sorted(supported_languages.keys()))
            )

        if message_dict:
            raise ValidationError(message_dict)

    def save(self, *args, **kwargs):
        global ACCESSIBLE_LANG_CACHE
        ACCESSIBLE_LANG_CACHE = {}

        if not self.description:
            self.description = supported_languages[self.code]

        super(Language, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"Language %s - %s" % (self.code, self.description)

    class Meta:
        app_label = 'pylucid'
        ordering = ("code",)
