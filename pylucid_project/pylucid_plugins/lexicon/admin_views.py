# coding:utf-8

from django import http
from django.utils.translation import ugettext_lazy as _

from pylucid_project.utils.site_utils import get_site_preselection

from pylucid_project.apps.pylucid.preference_forms import SystemPreferencesForm
from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid.markup.converter import apply_markup

from pylucid_project.apps.pylucid_admin.admin_menu import AdminMenu

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
    )

    return "\n".join(output)


@check_permissions(superuser_only=False, permissions=("lexicon.add_lexiconentry",))# "lexicon.add_links"))
@render_to("lexicon/new_entry.html")
def new_entry(request):
    """ create a new lexicon entry """
    context = {
        "title": _("Create a new lexicon entry"),
        "form_url": request.path,
    }

    if request.method == "POST":
        form = LexiconEntryForm(request.POST)
        if form.is_valid():
            if "preview" in request.POST:
                context["preview"] = apply_markup(
                    form.cleaned_data["content"], form.cleaned_data["markup"],
                    request.page_msg, escape_django_tags=True
                )
            else:
                instance = form.save()
                request.page_msg(_("Lexicon entry '%s' saved.") % instance.term)
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

