# coding: utf-8

"""
    Convert PageContent markup.
"""

from django import http
from django.conf import settings
from django.db import transaction
from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.models import PageContent, EditableHtmlHeadFile
from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid.markup import converter

from page_admin.forms import ConvertMarkupForm
from pylucid_project.utils.diff import get_pygmentize_diff



@check_permissions(superuser_only=False, permissions=("pylucid.change_pagecontent",))
@render_to("page_admin/convert_markup.html")
def convert_markup(request, pagecontent_id=None):
    """
    convert a PageContent markup
    """
    if not pagecontent_id:
        raise

    def _error(err):
        err_msg = _("Wrong PageContent ID.")
        if settings.DEBUG:
            err_msg += " (ID: %r, original error was: %r)" % (raw_PageContent_id, err)
        request.page_msg.error(err_msg)

    try:
        pagecontent_id = int(pagecontent_id)
    except Exception, err:
        return _error(err)

    try:
        pagecontent = PageContent.objects.get(id=pagecontent_id)
    except PageContent.DoesNotExist, err:
        return _error(err)

    absolute_url = pagecontent.get_absolute_url()
    context = {
        "title": _("Convert '%s' markup") % pagecontent.get_name(),
        "abort_url": absolute_url,
        "current_markup": pagecontent.MARKUP_DICT[pagecontent.markup],
        "pagecontent": pagecontent,
    }

    if request.method != "POST":
        form = ConvertMarkupForm(instance=pagecontent)
    else:
        form = ConvertMarkupForm(request.POST, instance=pagecontent)
        #request.page_msg(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            dest_markup_no = int(cleaned_data["dest_markup"])
            original_markup = cleaned_data["content"]
            try:
                new_markup = converter.convert_markup(
                    original_markup,
                    source_markup_no=pagecontent.markup,
                    dest_markup_no=dest_markup_no,
                    page_msg=request.page_msg
                )
            except Exception, err:
                request.page_msg.error("Convert error: %s" % err)
            else:
                if "preview" not in request.POST:
                    # Save converted markup and redirect to the updated page
                    sid = transaction.savepoint()
                    try:
                        pagecontent.content = new_markup
                        pagecontent.markup = dest_markup_no
                        pagecontent.save()
                    except:
                        transaction.savepoint_rollback(sid)
                        raise
                    else:
                        transaction.savepoint_commit(sid)
                        request.page_msg(_("Content page %r updated.") % pagecontent)
                        return http.HttpResponseRedirect(pagecontent.get_absolute_url())

                # preview markup convert:

                context["new_markup"] = new_markup

                converted_html = converter.apply_markup(
                    new_markup, dest_markup_no,
                    page_msg=request.page_msg, escape_django_tags=True
                )
                context["converted_html"] = converted_html

                if cleaned_data["verbose"]:
                    context["original_markup"] = original_markup

                    orig_html = converter.apply_markup(
                        original_markup, pagecontent.markup,
                        page_msg=request.page_msg, escape_django_tags=True
                    )
                    context["orig_html"] = orig_html

                    def strip_whitespace(html):
                        return "\n".join([line.strip() for line in html.splitlines() if line.strip()])

                    # Remove whitespace from html code.
                    orig_html2 = strip_whitespace(orig_html)
                    converted_html2 = strip_whitespace(converted_html)

                    if orig_html2 == converted_html2:
                        context["diff_is_the_same"] = True
                    else:
                        context["pygmentize_diff"] = get_pygmentize_diff(orig_html2, converted_html2)
                        try:
                            pygments_css = EditableHtmlHeadFile.on_site.get(filepath="pygments.css")
                        except EditableHtmlHeadFile.DoesNotExist:
                            request.page_msg("Error: No headfile with filepath 'pygments.css' found.")
                        else:
                            absolute_url = pygments_css.get_absolute_url(colorscheme=None)
                            context["pygments_css"] = absolute_url

    context.update({
        "form": form,
    })
    return context
