# coding: utf-8

"""
    i18n views
    ~~~~~~~~~~~
    
    TODO: move language views to this app!
    
    :copyleft: 2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django.utils.translation import ugettext as _
from django.contrib import messages
from django import http

from pylucid_project.apps.pylucid.models.language import Language
from pylucid_project.apps.i18n.forms import LanguageSelectForm


def select_language(request, cancel_url, source_language, source_entry_name):
    """
    choose the translation destination language.
    If only one other language is available -> return it directly.
    """
    if "cancel" in request.GET:
        messages.info(request, _("Choose translate aborted, ok."))
        return http.HttpResponseRedirect(cancel_url)

    other_languages = Language.objects.exclude(code=source_language.code)
    if len(other_languages) == 0:
        # should not happen
        messages.error(request, "Error: There exist only one Language!")
        return http.HttpResponseRedirect(cancel_url)
    elif len(other_languages) == 1:
        # Only one other language available, so the user must not choose one ;)
        return other_languages[0]
    else:
        # There are more than one other language -> display a form for choose one.
        if "language" in request.GET:
            form = LanguageSelectForm(other_languages, request.GET)
            if form.is_valid():
                lang_code = form.cleaned_data["language"]
                for lang in other_languages:
                    if lang.code == lang_code:
                        return lang
                raise RuntimeError() # should never happen
        else:
            default_lang_entry = Language.objects.get_or_create_default(request)
            form = LanguageSelectForm(other_languages, initial={
                    "language": default_lang_entry.code, # FIXME: Seems not to work
                })
        context = {
            "title": _("Select destination language for translation of '%(name)s' (%(desc_lang)s):") % {
                "name": source_entry_name,
                "desc_lang": source_language.description
            },
            "template_name": "i18n/select_translate_language.html",
            "form": form,
            "other_languages": other_languages,
        }
        return context
