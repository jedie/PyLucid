# coding: utf-8

"""
    PyLucid admin views
    ~~~~~~~~~~~~~~~~~~~

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django import http
from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to

from pylucid_project.apps.pylucid_admin.admin_menu import AdminMenu

from design.forms import SelectDesign
from pylucid_project.apps.pylucid.models import Design


def install(request):
    """ insert PyLucid admin views into PageTree """
    output = []

    admin_menu = AdminMenu(request, output)
    menu_section_entry = admin_menu.get_or_create_section("edit look")
    admin_menu.add_menu_entry(
        parent=menu_section_entry, url_name="Design-switch",
        name="switch design", title="Switch the page design, temporary.",
    )

    return "\n".join(output)


@check_permissions(superuser_only=False, permissions=("pylucid.change_design",))
@render_to("design/switch.html")
def switch(request):
    """
    'switch' the design.
    Save design ID in request.session["design_switch_pk"]
    This value would be used in design.signal_reveiver
    """
    context = {
        "title": _("Switch a PyLucid page design"),
        "form_url": request.path,
    }

    if "design_switch_pk" in request.session:
        design_id = request.session["design_switch_pk"]
        try:
            context["design_switch"] = Design.on_site.get(id=design_id)
        except Design.DoesNotExist, err:
            request.page_msg.error(_(
                    "Error: Design with ID %(id)r doesn't exist: %(err)s"
                ) % {"id":design_id, "err": err}
                )
            del request.session["design_switch_pk"]
            design_id = 0
    else:
        design_id = 0

    if request.method == "POST":
        form = SelectDesign(request.POST)
        if form.is_valid():
            design_id = int(form.cleaned_data["design"])
            if design_id == 0:
                # reset to automatic selection by pagetree association
                if "design_switch_pk" in request.session:
                    del request.session["design_switch_pk"]
                request.page_msg(
                    _("delete 'design switch', turn to automatic mode.")
                )
            else:
                request.page_msg(_("Save design ID %r") % design_id)
                request.session["design_switch_pk"] = design_id
            return http.HttpResponseRedirect(request.path)
    else:
        form = SelectDesign(initial={"design": design_id})

    context["form"] = form
    return context

