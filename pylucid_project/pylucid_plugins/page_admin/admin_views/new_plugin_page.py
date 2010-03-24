# coding:utf-8

from django import http
from django.conf import settings
from django.db import transaction
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.models import PageTree, Language
from pylucid_project.apps.pylucid.decorators import check_permissions, render_to

from page_admin.admin_views import _get_pagetree, _build_form_initial
from page_admin.forms import PageTreeForm, PageMetaForm, \
                                                             PluginPageForm




@check_permissions(superuser_only=False,
    permissions=("pylucid.add_pluginpage", "pylucid.add_pagemeta", "pylucid.add_pagetree")
)
@render_to("page_admin/edit_plugin_page.html")
def new_plugin_page(request):
    """
    Create a new plugin page.
    Create PageMeta in all existing languages.
    """
    context = {
        "title": _("Create a new plugin page"),
        "form_url": request.path,
        "abort_url": reverse("admin:index"),
    }

    languages = Language.objects.all()

    # Create for every language a own PageMeta model form.
    pagemeta_formset = []
    pagemeta_is_valid = True # Needed for check if all forms are valid.
    for lang in languages:
        if request.method == "POST":
            form = PageMetaForm(request.POST, prefix=lang.code)
            if not form.is_valid():
                pagemeta_is_valid = False
        else:
            form = PageMetaForm(prefix=lang.code)
        form.language = lang # for language info in fieldset legend
        pagemeta_formset.append(form)

    if request.method == "POST":
        pagetree_form = PageTreeForm(request.POST)
        pluginpage_form = PluginPageForm(request.POST)
        if pagemeta_is_valid and pagetree_form.is_valid() and pluginpage_form.is_valid():
            sid = transaction.savepoint()
            try:
                # Create new PageTree entry
                new_pagetree = pagetree_form.save(commit=False)
                new_pagetree.page_type = PageTree.PLUGIN_TYPE
                new_pagetree.save()

                # Create new PluginPage entry
                new_pluginpage = pluginpage_form.save(commit=False)
                new_pluginpage.pagetree = new_pagetree
                new_pluginpage.save() # needs primary key before a many-to-many relationship can be used.

                # Create all PageMeta entries and attach them to PluginPage
                new_pluginpage_instance = []
                for language, pagemeta_form in zip(languages, pagemeta_formset):
                    new_pagemeta = pagemeta_form.save(commit=False)
                    new_pagemeta.pagetree = new_pagetree
                    new_pagemeta.language = language
                    new_pagemeta.save()

            except:
                transaction.savepoint_rollback(sid)
                raise
            else:
                transaction.savepoint_commit(sid)
                request.page_msg(_("New plugin page %r created.") % new_pluginpage)
                return http.HttpResponseRedirect(new_pluginpage.get_absolute_url())
    else:
        parent_pagetree = _get_pagetree(request)
        if parent_pagetree:
            context["abort_url"] = parent_pagetree.get_absolute_url() # Go back to the cms page
            initial_data = _build_form_initial(request, parent_pagetree)
        else:
            initial_data = {}
        pagetree_form = PageTreeForm(initial=initial_data)
        pluginpage_form = PluginPageForm()

    # A list of all existing forms -> for form errorlist
    all_forms = pagemeta_formset[:] + [pluginpage_form, pagetree_form]

    context.update({
        "all_forms": all_forms, # For display the form error list from all existing forms.
        "has_errors": request.method == "POST", # At least one form has errors.
        # The forms:
        "pluginpage_form": pluginpage_form,
        "pagetree_form": pagetree_form,
        "pagemeta_formset": pagemeta_formset,
    })
    return context
