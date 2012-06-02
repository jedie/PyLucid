# coding: utf-8


"""
    PyLucid base models
    ~~~~~~~~~~~~~~~~~~~
    
    :copyleft: 2009-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.contrib import messages

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

# http://code.google.com/p/django-tools/
from django_tools.middlewares import ThreadLocal

from pylucid_project.utils import form_utils


TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"


class BaseModel(models.Model):
    def get_absolute_url(self):
        raise NotImplementedError
    get_absolute_url.short_description = _('absolute url')

    def get_site(self):
        raise NotImplementedError
    get_site.short_description = _('on site')

    def get_absolute_uri(self):
        """ returned the complete absolute URI (with the domain/host part) """
        request = ThreadLocal.get_current_request()
        is_secure = request.is_secure()
        if is_secure:
            protocol = "https://"
        else:
            protocol = "http://"
        site = self.get_site()
        domain = site.domain

        if "://" in domain:
            domain2 = domain.split("://", 1)[-1]
            msg = (
                "Wrong site domain %r: protocol should not inserted there!"
                " (Please change it to: %r)"
            ) % (domain, domain2)
            messages.error(request, msg)
            domain = domain2

        absolute_url = self.get_absolute_url()
        return protocol + domain + absolute_url
    get_absolute_uri.short_description = _('absolute uri')

    class Meta:
        abstract = True



class BaseModelManager(models.Manager):
    def easy_create(self, cleaned_form_data, extra={}):
        """
        Creating a new model instance with cleaned form data witch can hold more data than for
        this model needed.
        """
        keys = self.model._meta.get_all_field_names()
        model_kwargs = form_utils.make_kwargs(cleaned_form_data, keys)
        model_kwargs.update(extra)
        model_instance = self.model(**model_kwargs)
        model_instance.save()
        return model_instance

    def get_by_prefered_language(self, request, queryset, show_lang_errors=False):
        """
        return a item from queryset in this way:
        - try to get in language by client prefered order
        - if not exist: try to get in system default language
        - if not exist: use the first found item
        """
        item = None
        tried_languages = []
        languages = request.PYLUCID.languages # languages are in client prefered order
        for language in languages:
            try:
                item = queryset.get(language=language)
            except ObjectDoesNotExist:
                tried_languages.append(language)
            else:
                break

        if item is None:
            # Fallback and used the first found item
            try:
                item = queryset[0]
            except IndexError, err:
                raise self.model.DoesNotExist(err)

        if show_lang_errors:
            current_language = request.PYLUCID.current_language
            if item.language != current_language:
                try:
                    item2 = queryset.get(language=current_language)
                except ObjectDoesNotExist:
                    pass
                else:
                    msg = render_to_string("pylucid/includes/language_info_link.html",
                        {
                            "item": item2,
                            "language": current_language.description,
                        }
                    )
                    messages.info(request, msg)


        return item, tried_languages



