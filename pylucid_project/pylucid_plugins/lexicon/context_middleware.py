# -*- coding: utf-8 -*-

"""
    PyLucid breadcrumb plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Generates a horizontal backlink bar.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

__version__ = "$Rev:$"

from django.template import RequestContext
from django.template.loader import render_to_string

from tagging.utils import parse_tag_input

from pylucid_project.apps.pylucid.models import PageTree

#from breadcrumb.preference_forms import BreadcumbPrefForm
from lexicon.models import LexiconEntry

class ContextMiddleware(object):
    def __init__(self, request, context):
        self.request = request
        self.context = context

        # Get preferences
#        pref_form = BreadcumbPrefForm()
#        self.pref_data = pref_form.get_preferences()

        # Get all pages back to the root page as a list
#        self.linklist = PageTree.objects.get_backlist(request)

    def add_link(self, name, title, url):
        """ Can be called from plugins, to insert own virtual sub pages """
        self.linklist.append({"name": name, "title": title, "url": url})

    def render(self):
        page_content = self.context["page_content"]

        current_lang = self.request.PYLUCID.lang_entry
        queryset = LexiconEntry.on_site.filter(is_public=True).filter(lang=current_lang)
        entries = queryset.values_list("term", "alias", "short_definition")

        for term, alias, short_definition in entries:
            print term, alias, short_definition
            aliases = parse_tag_input(alias)
            print aliases
            terms = [term] + aliases
            for term in terms:
                spaced_term = " %s " % term
                if spaced_term not in page_content:
                    continue
                print "Found: %r" % spaced_term
                context = {
                    "term": term,
                    "short_definition": short_definition
                }
                html = render_to_string("lexicon/definition_link.html", context)
                page_content = page_content.replace(spaced_term, html)
                print page_content
                break

        self.context["page_content"] = page_content



#        context = {
#            "preferences": self.pref_data,
#            "linklist": self.linklist,
#        }
#        return render_to_response('breadcrumb/breadcrumb.html', context,
#            context_instance=RequestContext(self.request)
#        )
