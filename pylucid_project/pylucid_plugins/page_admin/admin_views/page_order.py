# coding: utf-8

from django import http
from django.conf import settings
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from pylucid_project.apps.pylucid.models import PageTree
from pylucid_project.apps.pylucid.decorators import check_permissions, render_to

from page_admin.forms import PageOrderFormSet



@check_permissions(superuser_only=False, permissions=("pylucid.change_pagetree",))
@render_to("page_admin/page_order.html")
def page_order(request, pagetree_id=None):
    """
    Change PageTree 'position', the ordering weight for sorting the pages in the menu.
    """
    try:
        pagetree = PageTree.on_site.get(id=pagetree_id)
    except PageTree.DoesNotExist, err:
        raise PageTree.DoesNotExist(
            "PageTree with ID %r doesn't exist. (Original error: %s)" % (pagetree_id, err)
        )
    parent = pagetree.parent

    queryset = PageTree.on_site.all().order_by("position")
    queryset = queryset.filter(parent=parent)

    if request.method == 'POST':
        formset = PageOrderFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            sid = transaction.savepoint()
            try:
                formset.save()
            except:
                transaction.savepoint_rollback(sid)
                raise
            transaction.savepoint_commit(sid)
            request.page_msg("New position saved.")
            return http.HttpResponseRedirect(request.path)
    else:
        formset = PageOrderFormSet(queryset=queryset)

    # Change field label ("position") to PageTree.slug
    for form in formset.forms:
        for field_name, field in form.fields.iteritems():
            field.label = form.instance.slug
            field.help_text = form.instance.get_absolute_url()

    context = {
        "title": "Change the page order.",
        "pagetree": pagetree,
        "abort_url": pagetree.get_absolute_url(),
        "formset": formset,
    }
    if parent is not None:
        context["previous_level"] = parent

    try:
        context["next_level"] = PageTree.on_site.order_by("position").filter(parent=pagetree)[0]
    except IndexError:
        pass

    return context

