# coding: utf-8

"""
    PyLucid admin views
    ~~~~~~~~~~~~~~~~~~~

    :copyleft: 2010-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import posixpath

from django import http
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.template.base import TemplateDoesNotExist
from django.template.loader import find_template_loader
from django.utils.translation import ugettext as _

from dbtemplates.models import Template as DBTemplateModel

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid.models import Design, Color, ColorScheme
from pylucid_project.apps.pylucid_admin.admin_menu import AdminMenu
from pylucid_project.utils.css_color_utils import unique_color_name

from .forms import SwitchDesignForm, CloneDesignForm


def install(request):
    """ insert PyLucid admin views into PageTree """
    output = []

    admin_menu = AdminMenu(request, output)
    menu_section_entry = admin_menu.get_or_create_section("edit look")
    admin_menu.add_menu_entry(
        parent=menu_section_entry, url_name="Design-switch",
        name="switch design", title="Switch the page design, temporary.",
    )
    admin_menu.add_menu_entry(
        parent=menu_section_entry, url_name="Design-clone",
        name="clone design",
        title="Clone a existing page design with all associated components.",
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
            messages.error(request, _(
                    "Error: Design with ID %(id)r doesn't exist: %(err)s"
                ) % {"id":design_id, "err": err}
                )
            del request.session["design_switch_pk"]
            design_id = 0
    else:
        design_id = 0

    if request.method == "POST":
        form = SwitchDesignForm(request.POST)
        if form.is_valid():
            design_id = int(form.cleaned_data["design"])
            if design_id == 0:
                # reset to automatic selection by pagetree association
                if "design_switch_pk" in request.session:
                    del request.session["design_switch_pk"]
                messages.info(request,
                    _("delete 'design switch', turn to automatic mode.")
                )
            else:
                messages.info(request, _("Save design ID %r") % design_id)
                request.session["design_switch_pk"] = design_id
            return http.HttpResponseRedirect(request.path)
    else:
        form = SwitchDesignForm(initial={"design": design_id})

    context["form"] = form
    return context


#------------------------------------------------------------------------------
# clone design


def get_template_source(template_name):
    """
    Return the source code of a template (not a compiled version)
    FIXME: Is there no django API for this?
    """
    for loader_name in settings.TEMPLATE_LOADERS:
        loader = find_template_loader(loader_name)
        if loader is None:
            continue
        try:
            template_source = loader.load_template_source(template_name)[0]
        except TemplateDoesNotExist:
            continue
        else:
            return template_source
    raise TemplateDoesNotExist(template_name)


def _clone_template(design, new_template_name, sites):
    """
    create a new DB-Template entry with the content from
    the design template
    """
    template_path = design.template
    source = get_template_source(template_path)
    new_template = DBTemplateModel(name=new_template_name, content=source)
    new_template.save(force_insert=True)
    new_template.sites = sites
    new_template.save(force_update=True)
    return new_template


def _clone_headfiles(design, new_name, sites):
    """ Clone all headfiles from the given source design. """
    new_headfiles = []
    old_headfiles = design.headfiles.all()
    for headfile in old_headfiles:
        old_filepath = headfile.filepath
        basename = posixpath.basename(old_filepath)
        new_filepath = posixpath.join(new_name, basename)

        headfile.pk = None # make the object "new" ;)
        headfile.filepath = new_filepath
        headfile.description += "\n(cloned from '%s')" % old_filepath
        headfile.save(force_insert=True)
        headfile.sites = sites
        headfile.save(force_update=True)

        new_headfiles.append(headfile)

    return new_headfiles


def _clone_colorscheme(design, new_name, sites):
    """
    Clone the colorscheme and all colors.
    """
    colorscheme = design.colorscheme
    if colorscheme is None:
        # design used no colorscheme
        return

    colors = Color.objects.filter(colorscheme=colorscheme)

    colorscheme.pk = None # make the object "new" ;)
    colorscheme.name = new_name
    colorscheme.save(force_insert=True)
    colorscheme.sites = sites
    colorscheme.save(force_update=True)

    for color in colors:
        color.pk = None # make the object "new" ;)
        color.colorscheme = colorscheme
        color.save(force_insert=True)
        color.sites = sites
        color.save(force_update=True)

    return colorscheme


@check_permissions(superuser_only=False, permissions=(
    "pylucid.add_design",
    "pylucid.add_editablehtmlheadfile",
    "pylucid.add_color",
    "pylucid.add_colorscheme",
    "dbtemplates.add_template",
    )
)
@render_to("design/clone.html")
def clone(request):
    context = {
        "title": _("Clone a existing page design with all associated components."),
        "form_url": request.path,
    }

    if request.method == "POST":
        form = CloneDesignForm(request.POST)
        if form.is_valid():
            messages.info(request, form.cleaned_data)

            new_name = form.cleaned_data["new_name"]
            sites = form.cleaned_data["sites"]

            design_id = int(form.cleaned_data["design"])
            design = Design.objects.get(id=design_id)

            new_template_name = form.get_new_template_name()
            new_template = _clone_template(design, new_template_name, sites)

            new_headfiles = _clone_headfiles(design, new_name, sites)

            new_colorscheme = _clone_colorscheme(design, new_name, sites)

            design.pk = None # make the object "new" ;)
            design.name = new_name
            design.template = new_template.name
            design.colorscheme = new_colorscheme
            design.save(force_insert=True)
            design.sites = sites
            design.headfiles = new_headfiles
            design.save(force_update=True)

            messages.success(request, _("New design '%s' created.") % new_name)
            return http.HttpResponseRedirect(request.path)
    else:
        form = CloneDesignForm()

    context["form"] = form
    return context


@check_permissions(superuser_only=False, permissions=(
    "pylucid.change_editablehtmlheadfile",
    "pylucid.change_color",
    )
)
def rename_colors(request, colorscheme_id):
    """
    TODO: display the changed colors in a form, so that the user
    can choose witch colors should really be renamed.
    """
    colorschmeme = ColorScheme.objects.get(id=colorscheme_id)
    colors = Color.objects.filter(colorscheme=colorschmeme)

    changed_colors = 0
    existing_colors = []
    for color in colors:
        hex_string = color.value
        old_color_name = color.name
        new_color_name = unique_color_name(existing_colors, hex_string)
        existing_colors.append(new_color_name) # needed to make names unique
        if new_color_name == old_color_name:
            # nothing to do
            continue
        color.name = new_color_name
        color.save()
        changed_colors += 1

    messages.info(request, "%s colors exist. %s changed" % (len(existing_colors), changed_colors))

    url = reverse("admin:pylucid_colorscheme_change", args=(colorscheme_id,))
    return http.HttpResponseRedirect(url)
