# coding: utf-8

"""
    Create a new content page.
"""

from django import http
from django.conf import settings
from django.db import transaction
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.models import PageTree, Language
from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid.markup.converter import apply_markup

from page_admin.admin_views import _get_pagetree, _build_form_initial
from page_admin.forms import PageTreeForm, PageMetaForm, \
                                                             PageContentForm




@check_permissions(superuser_only=False,
    permissions=("pylucid.add_pagecontent", "pylucid.add_pagemeta", "pylucid.add_pagetree")
)
@render_to("page_admin/edit_content_page.html")#, debug=True)
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
    default_lang_entry = Language.objects.get_or_create_default(request)
    context = {
        "title": _("Create a new page"),
        "default_lang_entry": default_lang_entry,
        "form_url": request.path,
        "abort_url": reverse("admin:index"),
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
                    url = new_pagecontent.get_absolute_url()
                    request.page_msg(_("New content page %r created.") % url)
                    return http.HttpResponseRedirect(url)
    else:
        parent_pagetree = _get_pagetree(request)
        if parent_pagetree:
            context["abort_url"] = parent_pagetree.get_absolute_url() # Go back to the cms page
            initial_data = _build_form_initial(request, parent_pagetree)
        else:
            initial_data = {}
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

        "pagelinklist_url": "#TODO",
    })
    return context

