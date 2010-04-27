# coding:utf-8

import os
import time
from datetime import datetime, timedelta


if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"
    virtualenv_file = "../../../../../bin/activate_this.py"
    execfile(virtualenv_file, dict(__file__=virtualenv_file))


from django import http
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.contrib.sessions.models import Session

from dbtemplates.models import Template

from pylucid_project.apps.pylucid.models import LogEntry
from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid.markup.hightlighter import make_html, get_pygments_css

from pylucid_project.apps.pylucid_admin.admin_menu import AdminMenu

from tools.forms import HighlightCodeForm, CleanupLogForm, SelectTemplateForm


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
    admin_menu.add_menu_entry(
        parent=menu_section_entry, name="overwrite template",
        title="Overwrite a filesystem template with a new database headfile entry",
        url_name="Tools-overwrite_template"
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

    # get the EditableHtmlHeadFile path to pygments.css (page_msg created, if not exists)
    pygments_css_path = get_pygments_css(request)
    context["pygments_css"] = pygments_css_path

    if request.method == "POST":
        form = HighlightCodeForm(request.POST)
        if form.is_valid():
            sourcecode = form.cleaned_data["sourcecode"]
            source_type = form.cleaned_data["source_type"]

            highlighted = make_html(sourcecode, source_type, django_escape=True)
            context["highlighted"] = highlighted

            html_code = make_html(highlighted, "html", django_escape=True)
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
            start_time = time.time()
            number = form.cleaned_data["number"]
            delete_type = form.cleaned_data["delete_type"]
            limit_site = form.cleaned_data["limit_site"]

            if limit_site:
                queryset = LogEntry.on_site
            else:
                queryset = LogEntry.objects

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

            delete_count = queryset.count()
            queryset.delete()
            duration_time = time.time() - start_time
            request.page_msg(_("Delete %(count)s entries in %(duration).2fsec") % {
                "count": delete_count, "duration":duration_time
            })
            return HttpResponseRedirect(request.path)
    else:
        form = CleanupLogForm()

    context["form"] = form
    return context


@check_permissions(superuser_only=True)
@render_to("tools/cleanup_session.html")
def cleanup_session(request):
    """ Delete old session entries """

    count_before = Session.objects.count()
    start_time = time.time()
    Session.objects.filter(expire_date__lt=datetime.now()).delete()
    duration_time = time.time() - start_time
    count_after = Session.objects.count()

    delete_count = count_before - count_after
    request.page_msg(_("Delete %(count)s entries in %(duration).2fsec") % {
        "count": delete_count, "duration":duration_time
    })

    context = {
        "title": _("Delete old session entries"),
        "count_before": count_before,
        "count_after": count_after,
        "count_deleted": delete_count,
    }
    return context


#-----------------------------------------------------------------------------------------------------------
# overwrite template


class TemplateFile(object):
    def __init__(self, request, fs_path):
        self.request = request
        self.fs_path = fs_path

        self.name = fs_path.rsplit("templates", 1)[1].lstrip("/")

    def _get_fs_content(self):
        try:
            f = file(self.fs_path, "r")
            content = f.read()
            f.close()
        except Exception, err:
            request.page_msg.error("Can't read file: %s" % err)
        else:
            return content

    def get_or_create_dbtemplate(self):
        """
        create a dbtemplate entry with the content form filesystem.
        return the dbtemplate instance if success, otherwise: create a page_msg and return None
        """
        content = self._get_fs_content()
        if not content:
            # Content can't readed.
            return

        template, created = Template.objects.get_or_create(name=self.name,
            defaults={"content": content}
        )
        if created:
            template.save()
            current_site = Site.objects.get_current()
            template.sites.add(current_site)
            template.save()
        return template, created

    def get_content_preview(self):
        content = self._get_fs_content()
        if not content:
            # Can't read the template content, page_msg was created.
            return

        ext = os.path.splitext(self.fs_path)[1]
        html = make_html(content, ext, django_escape=True)
        return html



@check_permissions(
    superuser_only=False,
    permissions=(u'dbtemplates.add_template', u'dbtemplates.change_template')
)
@render_to("tools/overwrite_template.html")
def overwrite_template(request):
    """
    Overwrite a template:
    1. The user can choose between all existing template in filesystem.
    2. Read the content from filesystem and create a new dbtemplate entry.
    3. redirect to edit the nre dbtemplate entry
    """
    context = {
        "title": _("overwrite template"),
        "form_url": request.path,
    }

    if request.method != "POST":
        form = SelectTemplateForm()
    else:
        form = SelectTemplateForm(request.POST)
        if form.is_valid():
            fs_path = form.cleaned_data["template"]
            template = TemplateFile(request, fs_path)

            if "preview" in request.POST:
                # Display only the template content
                preview_html = template.get_content_preview()
                if preview_html:
                    context["template"] = template

                    # get the EditableHtmlHeadFile path to pygments.css (page_msg created, if not exists)
                    pygments_css_path = get_pygments_css(request)
                    context["pygments_css"] = pygments_css_path
            else:
                # A new dbtemplate should be created
                instance, created = template.get_or_create_dbtemplate()
                if instance:
                    if created:
                        # New dbtemplate instance created -> edit it
                        # if instance == None: e.g.: error reading file -> page_msg was created
                        msg = _("New dbtemplate entry %s created.") % instance
                        LogEntry.objects.log_action(
                            app_label="pylucid_plugin.extrahead",
                            action="overwrite template %s" % template.name,
                            request=request,
                            message=msg
                        )
                    else:
                        msg = _("dbtemplate entry %s already exists!") % instance

                    msg += _(" You can edit it now.")

                    request.page_msg(msg)

                    # redirect to edit the new dbtemplate entry
                    url = reverse("admin:dbtemplates_template_change", args=(instance.id,))
                    return http.HttpResponseRedirect(url)

    context["form"] = form
    return context


if __name__ == "__main__":
    templates = [TemplateDir(dir) for dir in settings.TEMPLATE_DIRS]
