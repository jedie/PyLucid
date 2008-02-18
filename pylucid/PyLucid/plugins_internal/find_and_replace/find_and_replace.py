#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid find and replace
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Find/Replace in all CMS page content.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__= "$Rev:$"

import time

from django import newforms as forms
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

from PyLucid.models import Page
from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.tools.utils import escape
from PyLucid.tools.Diff import diff_lines

# How min/max long must a search term be?
MIN_TERM_LEN = 2
MAX_TERM_LEN = 150


class FindReplaceForm(forms.Form):
    # TODO: min und max should be saved in the prefereces.
    find_string = forms.CharField(
        min_length = MIN_TERM_LEN, max_length = MAX_TERM_LEN,
    )
    replace_string = forms.CharField(
        min_length = MIN_TERM_LEN, max_length = MAX_TERM_LEN,
    )
    simulate = forms.BooleanField(
        initial = True, help_text = _("Don't replace anything.")
    )


class find_and_replace(PyLucidBasePlugin):

    def find_and_replace(self):
        context = {}
        if self.request.method == 'POST':
            form = FindReplaceForm(self.request.POST)
            if form.is_valid():
                start_time = time.time()
                results, total_changes = self.do(**form.cleaned_data)
                context = {
                    "results": results,
                    "total_changes": total_changes,
                    "duration": time.time() - start_time,
                }
        else:
            form = FindReplaceForm()

        context["form"] = form
        self._render_template("find_and_replace", context)


    def do(self, find_string, replace_string, simulate):
        """
        Do the find/replace action.
        Returns a result list with diff information.
        """
        pages = Page.objects.all().filter(content__icontains=find_string)
        if len(pages) == 0:
            self.page_msg("No pages contains the string '%s'" % find_string)
            return None, None

        total_changes = 0
        results = []
        changed_pages = []
        for page in pages:
            old_content = page.content

            changes = old_content.count(find_string)
            total_changes += changes

            new_content = old_content.replace(find_string, replace_string)
            if not simulate:
                page.content = new_content
                page.save()
                changed_pages.append(page.name)

            diff = diff_lines(old_content, new_content)
            diff = escape(diff)
            diff = mark_safe(diff)
#            self.page_msg(diff)

            results.append({
                "page": page,
                "changes": changes,
                "diff": diff,
            })

        if not simulate:
            self.page_msg.green("Changed pages:")
            self.page_msg.green(", ".join(changed_pages))

#        self.page_msg(results)
        return results, total_changes




