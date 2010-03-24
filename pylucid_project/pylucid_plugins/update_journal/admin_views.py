# coding:utf-8

from datetime import datetime, timedelta
import time

from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import resolve
from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid_admin.admin_menu import AdminMenu

from update_journal.models import UpdateJournal
from update_journal.forms import CleanupUpdateJournalForm


def install(request):
    """ insert PyLucid admin views into PageTree """
    output = []

    admin_menu = AdminMenu(request, output)
    menu_section_entry = admin_menu.get_or_create_section("tools")

    admin_menu.add_menu_entry(
        parent=menu_section_entry,
        name="cleanup update journal", title="Delete dead links from update journal",
        url_name="UpdateJournal-cleanup"
    )

    return "\n".join(output)

#-----------------------------------------------------------------------------


@check_permissions(superuser_only=False,
    permissions=(u'update_journal.delete_updatejournal', u'update_journal.delete_pageupdatelistobjects')
)
@render_to("update_journal/cleanup.html")
def cleanup(request):
    """ Remove dead links and delete old entries from update journal """
    context = {
        "title": _("Remove dead links and delete old entries from update journal"),
        "form_url": request.path,
    }
    if request.method == "POST":
        form = CleanupUpdateJournalForm(request.POST)
        if "dead_entries" in request.POST:
            # remove only dead entries
            entries = UpdateJournal.on_site.all()
            bad_links_count = 0
            good_links_count = 0
            start_time = time.time()
            for entry in entries:
                url = entry.get_absolute_url()

                if "?" in url:
                    url = url.split("?", 1)[0] # remove GET parameters

                try:
                    resolve(url)
                except Exception, err:
                    entry.delete() #
                    bad_links_count += 1
                else:
                    good_links_count += 1

            duration_time = time.time() - start_time
            request.page_msg(
                "Checked links in %.2fsec.: %s bad links delete and %s good links found." % (
                    duration_time, bad_links_count, good_links_count
                )
            )
            return HttpResponseRedirect(request.path)

        elif form.is_valid():
            start_time = time.time()
            number = form.cleaned_data["number"]
            delete_type = form.cleaned_data["delete_type"]
            limit_site = form.cleaned_data["limit_site"]

            if limit_site:
                queryset = UpdateJournal.on_site
            else:
                queryset = UpdateJournal.objects

            queryset = queryset.order_by('-lastupdatetime')

            if delete_type == CleanupUpdateJournalForm.LAST_NUMBERS:
                ids = tuple(queryset[number:].values_list('id', flat=True))
                queryset = queryset.filter(id__in=ids)
            else:
                if delete_type == CleanupUpdateJournalForm.LAST_DAYS:
                    delta = timedelta(days=number)
                elif delete_type == CleanupUpdateJournalForm.LAST_HOURS:
                    delta = timedelta(hours=number)
                else:
                    raise AssertionError("Wrong delete_type") # should never happen

                now = datetime.now()
                datetime_filter = now - delta
                queryset = queryset.exclude(createtime__gte=datetime_filter)

            delete_count = queryset.count()
            queryset.delete()
            duration_time = time.time() - start_time
            request.page_msg("Delete %s entries in %.2fsec" % (delete_count, duration_time))
            return HttpResponseRedirect(request.path)
    else:
        form = CleanupUpdateJournalForm()

    context["count_on_site"] = UpdateJournal.on_site.count()
    context["count_total"] = UpdateJournal.objects.count()
    context["form"] = form
    return context
