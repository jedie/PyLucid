# coding:utf-8


"""
    Lexicon admin views
    ~~~~~~~~~~~~~~~~~~~
    
    :copyleft: 2010-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django import http
from django.conf import settings
from django.contrib import messages
from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid.models import PageMeta
from pylucid_project.apps.pylucid.models.pluginpage import PluginPage
from pylucid_project.apps.pylucid_admin.admin_menu import AdminMenu
from pylucid_project.utils.site_utils import get_site_preselection

from lexicon.forms import LexiconEntryForm
from lexicon.preference_forms import LexiconPrefForm



def install(request):
    """ insert PyLucid admin views into PageTree """
    output = []

    admin_menu = AdminMenu(request, output)
    menu_section_entry = admin_menu.get_or_create_section("create content")

    admin_menu.add_menu_entry(
        parent=menu_section_entry, url_name="Lexicon-new_entry",
        name="new lexicon entry", title="Create a new lexicon entry.",
        get_pagemeta=True,
    )

    return "\n".join(output)


def _extend_form_url(request, context):
    """
    setup form_url and abort_url
    TODO: Use this in new_content, new_blog, too!
    """
    if "pagemeta" not in request.GET:
        return context

    try:
        pagemeta_id = int(request.GET["pagemeta"])
    except ValueError, err:
        if settings.DEBUG:
            messages.error(request, "Wrong pagemeta ID: %s" % err)
        return context

    try:
        pagemeta = PageMeta.objects.get(id=pagemeta_id)
    except PageMeta.DoesNotExist, err:
        if settings.DEBUG:
            messages.error(request, "Can't get PageMeta: %s" % err)
    else:
        source_url = pagemeta.get_absolute_url()
        context["abort_url"] = source_url
        context["form_url"] += "?pagemeta=%i" % pagemeta_id

    return context


@check_permissions(superuser_only=False, permissions=("lexicon.add_lexiconentry",))# "lexicon.add_links"))
@render_to("lexicon/new_entry.html")
def new_entry(request):
    """ create a new lexicon entry """
    context = {
        "title": _("Create a new lexicon entry"),
        "form_url": request.path,
    }

    context = _extend_form_url(request, context)

    if request.method == "POST":
        if "cancel" in request.POST:
            messages.info(request, _("Create new lexicon entry aborted, ok."))
            try:
                url = PluginPage.objects.reverse("lexicon", viewname="Lexicon-summary")
            except urlresolvers.NoReverseMatch:
                messages.warning(request, _("Lexicon plugin page doesn't exists, yet. Please create."))
                url = "/"
            return http.HttpResponseRedirect(url)

        form = LexiconEntryForm(request.POST)
        if form.is_valid():
            instance = form.save()
            messages.info(request, _("Lexicon entry '%s' saved.") % instance.term)
            return http.HttpResponseRedirect(instance.get_absolute_url())
    else:
        # Get preferences
        pref_form = LexiconPrefForm()

        initial = {
            "sites": get_site_preselection(pref_form, request), # preselect sites field
            "language": request.PYLUCID.current_language.pk, # preselect current language
        }
        form = LexiconEntryForm(initial=initial)

    context["form"] = form
    return context

