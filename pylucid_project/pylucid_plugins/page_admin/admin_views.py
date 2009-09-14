# coding:utf-8

from django import forms, http
from django.conf import settings
from django.db import transaction
from django.core import urlresolvers
from django.template import RequestContext
from django.core.urlresolvers import reverse
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

from page_admin.forms import PageTreeForm, PageMetaForm, PageContentForm, PluginPageForm, LanguageSelectForm


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
    default_lang_entry = Language.objects.get_default()
    context = {
        "title": "Create a new page",
        "default_lang_entry": default_lang_entry,
        "form_url": request.path,
        "abort_url": "#FIXME",
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
                    new_pagemeta.pagetree = new_pagetree
                    new_pagemeta.language = default_lang_entry
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
        "abort_url": "#FIXME",

        "all_forms": all_forms, # For display the form error list from all existing forms.
        "has_errors": request.method == "POST", # At least one form has errors.
        # The forms:
        "pluginpage_form": pluginpage_form,
        "pagetree_form": pagetree_form,
        "pagemeta_formset": pagemeta_formset,
    }
    return context


@check_permissions(superuser_only=False, permissions=("pylucid.change_pagecontent",))
def _edit_content_page(request, context, pagetree):
    """ edit a PageContent """
    default_lang_entry = Language.objects.get_default()
    pagemeta = PageTree.objects.get_pagemeta(request, pagetree, show_lang_errors=True)
    pagecontent = PageContent.objects.get(pagemeta=pagemeta)

    if request.method != "POST":
        pagetree_form = PageTreeForm(instance=pagetree)
        pagemeta_form = PageMetaForm(instance=pagemeta, prefix=default_lang_entry.code)
        pagecontent_form = PageContentForm(instance=pagecontent)
    else:
        pagetree_form = PageTreeForm(request.POST, instance=pagetree)
        pagemeta_form = PageMetaForm(request.POST, instance=pagemeta, prefix=default_lang_entry.code)
        pagecontent_form = PageContentForm(request.POST, instance=pagecontent)
        if not (pagetree_form.is_valid() and pagemeta_form.is_valid() and pagecontent_form.is_valid()):
            context["has_errors"] = True
        else:
            if "preview" in request.POST:
                context["preview"] = apply_markup(
                    pagecontent_form.cleaned_data["content"],
                    pagecontent_form.cleaned_data["markup"],
                    request.page_msg, escape_django_tags=True
                )
                context["has_errors"] = False
            else: # All forms are valid and it's not a preview -> Save all.
                sid = transaction.savepoint()
                try:
                    pagetree_form.save()
                    pagemeta_form.save()
                    pagecontent_form.save()
                except:
                    transaction.savepoint_rollback(sid)
                    raise
                else:
                    transaction.savepoint_commit(sid)
                    request.page_msg("Content page %r updated." % pagecontent)
                    return http.HttpResponseRedirect(pagecontent.get_absolute_url())

    # A list of all existing forms -> for form errorlist
    all_forms = [pagecontent_form, pagemeta_form, pagetree_form]

    context.update({
        "title": _("Edit a content page"),
        "template_name": EDIT_CONTENT_TEMPLATE,
        "abort_url": pagecontent.get_absolute_url(),

        "all_forms": all_forms, # For display the form error list from all existing forms.

        "pagetree_form": pagetree_form,
        "pagemeta_form":pagemeta_form,
        "pagecontent_form": pagecontent_form,

        "taglist_url": "#TODO",
        "pagelinklist_url": "#TODO",
    })
    return context


@check_permissions(superuser_only=False, permissions=("pylucid.change_pluginpage",))
def _edit_plugin_page(request, context, pagetree):
    """ edit a PluginPage entry with PageMeta in all Languages """

    pagemetas = PageMeta.objects.filter(pagetree=pagetree)
    pluginpage = PluginPage.objects.get(pagetree=pagetree)

    # Create for every language a own PageMeta model form.
    pagemeta_formset = []
    pagemeta_is_valid = True # Needed for check if all forms are valid.
    for pagemeta in pagemetas:
        if request.method == "POST":
            form = PageMetaForm(request.POST, prefix=pagemeta.language.code, instance=pagemeta)
            if not form.is_valid():
                pagemeta_is_valid = False
        else:
            form = PageMetaForm(prefix=pagemeta.language.code, instance=pagemeta)
        form.language = pagemeta.language # for language info in fieldset legend
        pagemeta_formset.append(form)

    if request.method == "POST":
        pagetree_form = PageTreeForm(request.POST, instance=pagetree)
        pluginpage_form = PluginPageForm(request.POST, instance=pluginpage)
        if pagemeta_is_valid and pagetree_form.is_valid() and pluginpage_form.is_valid():
            sid = transaction.savepoint()
            try:
                pagetree_form.save()
                pluginpage_form.save()

                # Save all PageMeta entries and attach them to PluginPage
                new_pluginpage_instance = []
                for pagemeta_form in pagemeta_formset:
                    pagemeta_form.save()
            except:
                transaction.savepoint_rollback(sid)
                raise
            else:
                transaction.savepoint_commit(sid)
                request.page_msg("Plugin page %r updated." % pluginpage)
                return http.HttpResponseRedirect(pluginpage.get_absolute_url())
    else:
        pagetree_form = PageTreeForm(instance=pagetree)
        pluginpage_form = PluginPageForm(instance=pluginpage)

    # A list of all existing forms -> for form errorlist
    all_forms = pagemeta_formset[:] + [pluginpage_form, pagetree_form]

    context = {
        "title": _("Edit a plugin page"),
        "template_name": EDIT_PLUGIN_TEMPLATE,
        "abort_url": pluginpage.get_absolute_url(),

        "all_forms": all_forms, # For display the form error list from all existing forms.
        "has_errors": request.method == "POST", # At least one form has errors.
        # The forms:
        "pluginpage_form": pluginpage_form,
        "pagetree_form": pagetree_form,
        "pagemeta_formset": pagemeta_formset,
    }
    return context


@check_permissions(superuser_only=False, permissions=("pylucid.change_pagetree", "pylucid.change_pagemeta"))
@render_to()
def edit_page(request, pagetree_id=None):
    """
    edit a PageContent or a PluginPage.
    """
    if not pagetree_id:
        raise

    pagetree = PageTree.objects.get(id=pagetree_id)

    context = {
        "form_url": request.path,
    }

    is_pluginpage = pagetree.page_type == PageTree.PLUGIN_TYPE
    if is_pluginpage:
#        return _edit_plugin_page(request)

        return _edit_plugin_page(request, context, pagetree)
    else:
        return _edit_content_page(request, context, pagetree)


def _select_language(request, context, source_pagemeta):
    """
    choose the translation destination language.
    If one one other language available -> return it directly.
    """
    other_languages = Language.objects.exclude(code=source_pagemeta.language.code)
    if len(other_languages) == 0:
        # should not happend
        request.page_msg.error("Error: There exist only one Language!")
        return http.HttpResponseRedirect(source_pagemeta.get_absolute_url())
    elif len(other_languages) == 1:
        # Only one other language available, so the user must not choose one ;)
        return other_languages[0]
    else:
        # There are more than one other language -> display a form for choose one.
        if "language" in request.GET:
            form = LanguageSelectForm(other_languages, request.GET)
            if form.is_valid():
                lang_code = form.cleaned_data["language"]
                for lang in other_languages:
                    if lang.code == lang_code:
                        return lang
                raise RuntimeError() # should never happen
        else:
            default_lang_entry = Language.objects.get_default()
            form = LanguageSelectForm(other_languages, initial={
                    "language": default_lang_entry.code, # FIXME: Seems not to work
                })
        context.update({
            "title": _("Translate page '%s' (%s) - Select destination language") % (
                source_pagemeta.name, source_pagemeta.language.description
            ),
            "template_name": "page_admin/select_translate_language.html",
            "form": form,
        })
        return context


@check_permissions(superuser_only=False, permissions=(
    "pylucid.add_pagecontent", "pylucid.add_pagemeta",
    "pylucid.change_pagecontent", "pylucid.change_pagemeta",
))
@render_to()
def translate(request, pagemeta_id=None):
    if not pagemeta_id:
        raise

    source_pagemeta = PageMeta.objects.get(id=pagemeta_id)
    pagetree = source_pagemeta.pagetree
    source_language = source_pagemeta.language

    is_pluginpage = pagetree.page_type == PageTree.PLUGIN_TYPE
    if is_pluginpage:
        request.page_msg.error("TODO: Translate a plugin page!")
        return http.HttpResponseRedirect(source_pagemeta.get_absolute_url())
    else:
        source_pagecontent = PageContent.objects.get(pagemeta=source_pagemeta)

    context = {
        "abort_url": source_pagemeta.get_absolute_url(),
    }

    # select the destination languare
    result = _select_language(request, context, source_pagemeta)
    if isinstance(result, Language):
        # Language was selected or they exit only one other language
        dest_language = result
    elif isinstance(result, dict):
        # template context returned -> render language select form
        return result
    elif isinstance(result, http.HttpResponse):
        # e.g. error
        return result
    else:
        raise RuntimeError() # Should never happen


    context.update({
        "title": _("Translate page '%s' (%s) into %s.") % (
            source_pagemeta.name, source_pagemeta.language.description, dest_language.description
        ),
        "template_name": "page_admin/translate_page.html",
    })

    try:
        dest_pagemeta = PageMeta.objects.get(pagetree=pagetree, language=dest_language)
    except PageMeta.DoesNotExist:
        dest_pagemeta = None
    else:
        dest_pagecontent = PageContent.objects.get(pagemeta=dest_pagemeta)

    if request.method == "POST":
        source_pagemeta_form = PageMetaForm(
            request.POST, prefix="source", instance=source_pagemeta
        )
        source_pagecontent_form = PageContentForm(
            request.POST, prefix="source", instance=source_pagecontent
        )
        if dest_pagemeta is None:
            dest_pagemeta_form = PageMetaForm(request.POST, prefix="dest")
            dest_pagecontent_form = PageContentForm(request.POST, prefix="dest")
        else:
            dest_pagemeta_form = PageMetaForm(
                request.POST, prefix=dest_language.code, instance=dest_pagemeta
            )
            dest_pagecontent_form = PageContentForm(
                request.POST, prefix=dest_language.code, instance=dest_pagecontent
            )

        if not (source_pagemeta_form.is_valid() and source_pagecontent_form.is_valid() and
                            dest_pagemeta_form.is_valid() and dest_pagecontent_form.is_valid()):
            context["has_errors"] = True
        else:
            context["has_errors"] = False
            if "preview" in request.POST:
                context["source_preview"] = apply_markup(
                    source_pagecontent_form.cleaned_data["content"],
                    source_pagecontent_form.cleaned_data["markup"],
                    request.page_msg, escape_django_tags=True
                )
                context["dest_preview"] = apply_markup(
                    dest_pagecontent_form.cleaned_data["content"],
                    dest_pagecontent_form.cleaned_data["markup"],
                    request.page_msg, escape_django_tags=True
                )
                context["has_errors"] = False
            else: # All forms are valid and it's not a preview -> Save all.
                sid = transaction.savepoint()
                try:
                    source_pagecontent_form.save()
                    source_pagemeta_form.save()

                    # Create new PageMeta entry
                    new_pagemeta = dest_pagemeta_form.save(commit=False)
                    new_pagemeta.pagetree = pagetree
                    new_pagemeta.language = dest_language
                    new_pagemeta.save()

                    # Create new PageContent entry
                    new_pagecontent = dest_pagecontent_form.save(commit=False)
                    new_pagecontent.pagemeta = new_pagemeta
                    new_pagecontent.save()
                except:
                    transaction.savepoint_rollback(sid)
                    raise
                else:
                    transaction.savepoint_commit(sid)
                    if dest_pagemeta is None:
                        request.page_msg("New content %r crerated." % new_pagecontent)
                    else:
                        request.page_msg("All updated.")
                    return http.HttpResponseRedirect(new_pagemeta.get_absolute_url())
    else:
        context["has_errors"] = False
        source_pagemeta_form = PageMetaForm(
            prefix="source", instance=source_pagemeta
        )
        source_pagecontent_form = PageContentForm(
            prefix="source", instance=source_pagecontent
        )
        if dest_pagemeta is None:
            dest_pagemeta_form = PageMetaForm(
                prefix="dest", initial={
                    "robots": source_pagemeta.robots,
                    "permitViewGroup": source_pagemeta.permitViewGroup, # FIXME: Doesn't work
                }
            )
            dest_pagecontent_form = PageContentForm(
                prefix="dest", initial={
                    "markup": source_pagecontent.markup,
                }
            )
        else:
            dest_pagemeta_form = PageMetaForm(
                prefix=dest_language.code, instance=dest_pagemeta
            )
            dest_pagecontent_form = PageContentForm(
                prefix=dest_language.code, instance=dest_pagecontent
            )

    source_pagecontent_form.language = source_language
    dest_pagecontent_form.language = dest_language

    pagemeta_fields = []
    for source_field, dest_field in zip(source_pagemeta_form, dest_pagemeta_form):
        source_field.language = source_language
        pagemeta_fields.append(source_field)
        dest_field.language = dest_language
        pagemeta_fields.append(dest_field)

    context.update({
        "all_forms": [
            source_pagemeta_form, source_pagecontent_form,
            dest_pagemeta_form, dest_pagecontent_form
        ],
        "source_pagemeta_form": source_pagemeta_form,
        "source_pagecontent_form": source_pagecontent_form,
        "dest_pagemeta_form": dest_pagemeta_form,
        "dest_pagecontent_form": dest_pagecontent_form,

        "pagemeta_fields": pagemeta_fields,
    })
    return context
