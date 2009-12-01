# coding:utf-8

from datetime import datetime, timedelta

from django import http
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.sessions.models import Session

from pylucid.models import EditableHtmlHeadFile, LogEntry
from pylucid.decorators import check_permissions, render_to

from pylucid_admin.admin_menu import AdminMenu

from pylucid.markup.hightlighter import make_html

from pylucid_project.pylucid_plugins.tools.forms import HighlightCodeForm, CleanupLogForm

MYSQL_ENCODING_VARS = (
    "character_set_server", "character_set_connection", "character_set_results", "collation_connection",
)


def install(request):
    """ insert PyLucid admin views into PageTree """
    output = []

    admin_menu = AdminMenu(request, output)
    menu_section_entry = admin_menu.get_or_create_section("tools")

    admin_menu.add_menu_entry(
        parent=menu_section_entry,
        name="highlight code", title="highlight sourcecode with pygments",
        url_name="Tools-highlight_code"
    )
    admin_menu.add_menu_entry(
        parent=menu_section_entry,
        name="cleanup log table", title="Cleanup the log table",
        url_name="Tools-cleanup_log"
    )
    admin_menu.add_menu_entry(
        parent=menu_section_entry,
        name="cleanup session table", title="Cleanup the session table",
        url_name="Tools-cleanup_session"
    )

    return "\n".join(output)

#-----------------------------------------------------------------------------

@check_permissions(superuser_only=False, permissions=(u'pylucid.change_pagecontent',))
@render_to("tools/highlight_code.html")
def highlight_code(request):
    """ hightlight sourcecode for copy&paste """
    context = {
        "title": _("hightlight sourcecode"),
        "form_url": request.path,
    }

    try:
        pygments_css = EditableHtmlHeadFile.on_site.get(filepath="pygments.css")
    except EditableHtmlHeadFile.DoesNotExist:
        request.page_msg("Error: No headfile with filepath 'pygments.css' found.")
    else:
        absolute_url = pygments_css.get_absolute_url(colorscheme=None)
        context["pygments_css"] = absolute_url

    if request.method == "POST":
        form = HighlightCodeForm(request.POST)
        if form.is_valid():
            sourcecode = form.cleaned_data["sourcecode"]
            source_type = form.cleaned_data["source_type"]

            highlighted = make_html(sourcecode, source_type)
            context["highlighted"] = highlighted

            html_code = make_html(highlighted, "html")
            context["html_code"] = html_code
    else:
        form = HighlightCodeForm()

    context["form"] = form
    return context



@check_permissions(superuser_only=True)
@render_to("tools/cleanup_log.html")
def cleanup_log(request):
    """ Delete old log entries """
    context = {
        "title": _("Delete old log entries"),
        "form_url": request.path,
        "count_on_site": LogEntry.on_site.count(),
        "count_total": LogEntry.objects.count(),
        "oldest_on_site_entry": LogEntry.on_site.all().only("createtime").order_by('createtime')[0],
        "oldest_total_entry": LogEntry.objects.all().only("createtime").order_by('createtime')[0],
    }
    if request.method == "POST":
        form = CleanupLogForm(request.POST)
        if form.is_valid():
            number = form.cleaned_data["number"]
            delete_type = form.cleaned_data["delete_type"]
            limit_site = form.cleaned_data["limit_site"]

            if limit_site:
                queryset = LogEntry.on_site.all()
            else:
                queryset = LogEntry.objects.all()

            queryset = queryset.order_by('-createtime')

            if delete_type == CleanupLogForm.LAST_NUMBERS:
                ids = tuple(queryset[number:].values_list('id', flat=True))
                queryset = queryset.filter(id__in=ids)
            else:
                if delete_type == CleanupLogForm.LAST_DAYS:
                    delta = timedelta(days=number)
                elif delete_type == CleanupLogForm.LAST_HOURS:
                    delta = timedelta(hours=number)
                else:
                    raise AssertionError("Wrong delete_type") # should never happen

                now = datetime.now()
                datetime_filter = now - delta
                queryset = queryset.exclude(createtime__gte=datetime_filter)

            request.page_msg("Delete %s entries." % queryset.count())
            queryset.delete()
            return http.HttpResponseRedirect(request.path)
    else:
        form = CleanupLogForm()

    context["form"] = form
    return context


@check_permissions(superuser_only=True)
@render_to("tools/cleanup_session.html")
def cleanup_session(request):
    """ Delete old session entries """

    count_before = Session.objects.count()
    Session.objects.filter(expire_date__lt=datetime.now()).delete()
    count_after = Session.objects.count()

    context = {
        "title": _("Delete old session entries"),
        "count_before": count_before,
        "count_after": count_after,
        "count_deleted": count_before - count_after,
    }
    return context
