# coding:utf-8

from django import forms, http
from django.conf import settings
from django.db import transaction
from django.core import urlresolvers
from django.template import RequestContext
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _

from pylucid_project.utils.form_utils import make_kwargs

from pylucid.models import PageTree, PageMeta, PageContent, Design, Language, PluginPage
from pylucid.preference_forms import SystemPreferencesForm
from pylucid.decorators import check_permissions, render_to
from pylucid.markup.converter import apply_markup

from pylucid_admin.admin_menu import AdminMenu

from page_admin.forms import PageTreeForm, PageMetaForm, PageContentForm, PluginPageForm


EDIT_PLUGIN_TEMPLATE = "page_admin/edit_plugin_page.html"
EDIT_CONTENT_TEMPLATE = "page_admin/edit_content_page.html"



def install(request):
    """ insert PyLucid admin views into PageTree """
    output = []

    admin_menu = AdminMenu(request, output)
    menu_section_entry = admin_menu.get_or_create_section("create content")

    admin_menu.add_menu_entry(
        parent=menu_section_entry, url_name="PageAdmin-new_content_page",
        name="new content page", title="Create a new content page.",
        get_pagetree=True
    )
    admin_menu.add_menu_entry(
        parent=menu_section_entry, url_name="PageAdmin-new_plugin_page",
        name="new plugin page", title="Create a new plugin page.",
        get_pagetree=True
    )

    return "\n".join(output)


def _build_form_initial(request):
    """
    Build a initial dict for preselecting some form fields.
    """
    initial_data = {}

    raw_pagetree_id = request.GET.get("pagetree")
    if not raw_pagetree_id:
        return {}

    err_msg = "Wrong PageTree ID."

    try:
        pagetree_id = int(raw_pagetree_id)
    except Exception, err:
        if settings.DEBUG:
            err_msg += " (ID: %r, original error was: %r)" % (raw_pagetree_id, err)
        request.page_msg.error(err_msg)
        return {}

    try:
        parent_pagetree = PageTree.on_site.get(id=pagetree_id)
    except PageTree.DoesNotExist, err:
        if settings.DEBUG:
            err_msg += " (ID: %r, original error was: %r)" % (pagetree_id, err)
        request.page_msg.error(err_msg)
        return {}

    info_msg = "preselect some values from %r" % parent_pagetree.get_absolute_url()
    if settings.DEBUG:
        info_msg += " (PageTree: %r)" % parent_pagetree
    request.page_msg.info(info_msg)

    for attr_name in ("parent", "design", "showlinks", "permitViewGroup", "permitEditGroup"):
        model_attr = getattr(parent_pagetree, attr_name)
        if hasattr(model_attr, "pk"):
            # XXX: Why must we discover the ID here? A django Bug?
            initial_data[attr_name] = model_attr.pk
        else:
            initial_data[attr_name] = model_attr

    return initial_data




@check_permissions(superuser_only=False,
    permissions=("pylucid.add_pagecontent", "pylucid.add_pagemeta", "pylucid.add_pagetree")
)
@render_to(EDIT_CONTENT_TEMPLATE)#, debug=True)
def new_content_page(request):
    """
    Create a new content page.
    
    TODO:
        * setup design via ajax, if not set and a parent page tree was selected
        * Auto generate slug from page name with javascript
    
    can use django.forms.models.inlineformset_factory:
        PageFormSet = inlineformset_factory(PageTree, PageContent, PageMeta)
    get:
        metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of
        the metaclasses of all its bases
    see also: http://code.djangoproject.com/ticket/7837
    """
    default_lang_entry = request.PYLUCID.default_lang_entry
    context = {
        "title": "Create a new page",
        "default_lang_entry": request.PYLUCID.default_lang_entry,
        "form_url": request.path,
        "has_errors": request.method == "POST", # At least one form has errors.
    }

    if request.method == "POST":
        pagetree_form = PageTreeForm(request.POST)
        pagemeta_form = PageMetaForm(request.POST, prefix=default_lang_entry.code)
        pagecontent_form = PageContentForm(request.POST)
        if pagetree_form.is_valid() and pagemeta_form.is_valid() and pagecontent_form.is_valid():
            if "preview" in request.POST:
                context["preview"] = apply_markup(
                    pagecontent_form.cleaned_data["content"],
                    pagecontent_form.cleaned_data["markup"],
                    request.page_msg, escape_django_tags=True
                )
                context["has_errors"] = False
            else:
                sid = transaction.savepoint()
                try:
                    # Create new PageTree entry
                    new_pagetree = pagetree_form.save(commit=False)
                    new_pagetree.page_type = PageTree.PAGE_TYPE
                    new_pagetree.save()

                    # Create new PageMeta entry
                    new_pagemeta = pagemeta_form.save(commit=False)
                    new_pagemeta.page = new_pagetree
                    new_pagemeta.lang = default_lang_entry
                    new_pagemeta.save()

                    # Create new PageContent entry
                    new_pagecontent = pagecontent_form.save(commit=False)
                    new_pagecontent.pagemeta = new_pagemeta
                    new_pagecontent.save()
                except:
                    transaction.savepoint_rollback(sid)
                    raise
                else:
                    transaction.savepoint_commit(sid)
                    request.page_msg("New content page %r created." % new_pagecontent)
                    return http.HttpResponseRedirect(new_pagecontent.get_absolute_url())
    else:
        initial_data = _build_form_initial(request)
        pagetree_form = PageTreeForm(initial=initial_data)
        pagemeta_form = PageMetaForm(prefix=default_lang_entry.code)
        pagecontent_form = PageContentForm()

    # A list of all existing forms -> for form errorlist
    all_forms = [pagecontent_form, pagemeta_form, pagetree_form]

    context.update({
        "all_forms": all_forms, # For display the form error list from all existing forms.

        "pagetree_form": pagetree_form,
        "pagemeta_form":pagemeta_form,
        "pagecontent_form": pagecontent_form,

        "taglist_url": "#TODO",
        "pagelinklist_url": "#TODO",
    })
    return context



@check_permissions(superuser_only=False,
    permissions=("pylucid.add_pluginpage", "pylucid.add_pagemeta", "pylucid.add_pagetree")
)
@render_to(EDIT_PLUGIN_TEMPLATE)
def new_plugin_page(request):
    """
    Create a new plugin page.
    Create PageMeta in all existing languages.
    """
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
        form.lang = lang # for language info in fieldset legend
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
                new_pluginpage.save() # needs primary key before a many-to-many relationship can be used.

                # Create all PageMeta entries and attach them to PluginPage
                new_pluginpage_instance = []
                for language, pagemeta_form in zip(languages, pagemeta_formset):
                    new_pagemeta = pagemeta_form.save(commit=False)
                    new_pagemeta.page = new_pagetree
                    new_pagemeta.lang = language
                    new_pagemeta.save()
                    new_pluginpage.pagemeta.add(new_pagemeta)

                new_pluginpage.save()
            except:
                transaction.savepoint_rollback(sid)
                raise
            else:
                transaction.savepoint_commit(sid)
                request.page_msg("New plugin page %r created." % new_pluginpage)
                return http.HttpResponseRedirect(new_pluginpage.get_absolute_url())
    else:
        initial_data = _build_form_initial(request)
        pagetree_form = PageTreeForm(initial=initial_data)
        pluginpage_form = PluginPageForm()

    # A list of all existing forms -> for form errorlist
    all_forms = pagemeta_formset[:] + [pluginpage_form, pagetree_form]

    context = {
        "title": "Create a new plugin page",
        "form_url": request.path,

        "all_forms": all_forms, # For display the form error list from all existing forms.
        "has_errors": request.method == "POST", # At least one form has errors.
        # The forms:
        "pluginpage_form": pluginpage_form,
        "pagetree_form": pagetree_form,
        "pagemeta_formset": pagemeta_formset,
    }
    return context


@check_permissions(superuser_only=False,
    permissions=("pylucid.change_pagemeta", "pylucid.change_pagetree")
)
@render_to()
def edit_page(request, pagetree_id=None):
    """
    edit a PageContent or a PluginPage.
    """
    request.page_msg("TODO: Implement the save routine.")
    request.page_msg("FIXME: Why does the form not fill all existing data, e.g: design, parent fields etc.")

    if not pagetree_id:
        raise

    pagetree = PageTree.objects.get(id=pagetree_id)

    context = {}

    is_pluginpage = pagetree.page_type == PageTree.PLUGIN_TYPE

    if is_pluginpage:
        if not request.user.has_perms("pylucid.change_pluginpage"):
            raise PermissionDenied("You have not the permission to change a plugin page!")
        Form = PluginPageForm
        context.update({
            "title": "Edit plugin page",
            "template_name": EDIT_PLUGIN_TEMPLATE,
        })
    else:
        if not request.user.has_perms("pylucid.change_pagecontent"):
            raise PermissionDenied("You have not the permission to change a content page!")
        Form = PageContentForm
        context.update({
            "title": "Edit content page",
            "template_name": EDIT_CONTENT_TEMPLATE,
        })

    if request.method == "POST":
        form = Form(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            request.page_msg(cleaned_data)
    else:
        pagemeta = PageTree.objects.get_pagemeta(request, pagetree, show_lang_info=True)
        form_models = [pagetree, pagemeta]
        if is_pluginpage:
            pluginpage = PluginPage.objects.get(page=pagetree)
            form_models.append(pluginpage)
        else:
            pagecontent = PageTree.objects.get_pagecontent(request, pagetree, show_lang_info=True)
            form_models.append(pagecontent)

        form_base_fields = Form.base_fields.keys()
        form_data = {}
        for model in form_models:
            keys = model._meta.get_all_field_names()
            for key in keys:
                if key not in form_base_fields:
                    continue
                value = getattr(model, key)
                #request.page_msg("*", key, value)
                form_data[key] = value

        form = Form(initial=form_data)

#    from django.forms.models import inlineformset_factory
#    FormSet = inlineformset_factory(PageTree, PageMeta, extra=1)
#    form = FormSet(instance=pagetree)

    context.update({
        "form_url": request.path,
        "form": form,
    })
    return context
