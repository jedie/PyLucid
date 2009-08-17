# coding: utf-8

__version__ = "$Rev:$"

from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from tagging.utils import parse_tag_input

from pylucid_project.apps.pylucid.models import PageTree

from lexicon.models import LexiconEntry


def pre_render_global_template_handler(**kwargs):
    request = kwargs["request"]

    current_lang = request.PYLUCID.lang_entry
    page_content = request.PYLUCID.context["page_content"]

    queryset = LexiconEntry.on_site.filter(is_public=True).filter(lang=current_lang)
    entries = queryset.values_list("term", "alias", "short_definition")

    for term, alias, short_definition in entries:
        aliases = parse_tag_input(alias) # Split django-tagging field value into a python list

        all_terms = [term] + aliases
        for term in all_terms:
            spaced_term = " %s " % term
            if spaced_term not in page_content:
                continue

            context = {
                "term": term,
                "short_definition": short_definition
            }
            html = render_to_string("lexicon/definition_link.html", context)
            html = " %s " % html.strip()
            page_content = page_content.replace(spaced_term, html)
            break

    if page_content != request.PYLUCID.context["page_content"]:
        page_content = mark_safe(page_content)
        request.PYLUCID.context["page_content"] = page_content

