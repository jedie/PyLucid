# coding:utf-8

from django.conf import settings
from django.utils.translation import ugettext as _

from pylucid.models import EditableHtmlHeadFile
from pylucid.decorators import check_permissions, render_to

from pylucid_admin.admin_menu import AdminMenu

from pylucid.markup.hightlighter import make_html

from pylucid_project.pylucid_plugins.tools.forms import HighlightCodeForm

MYSQL_ENCODING_VARS = (
    "character_set_server", "character_set_connection", "character_set_results", "collation_connection",
)


def install(request):
    """ insert PyLucid admin views into PageTree """
    output = []

    admin_menu = AdminMenu(request, output)
    menu_section_entry = admin_menu.get_or_create_section("tools")

    admin_menu.add_menu_entry(
        parent=menu_section_entry,
        name="highlight code", title="highlight sourcecode with pygments",
        url_name="Tools-highlight_code"
    )

    return "\n".join(output)

#-----------------------------------------------------------------------------

@check_permissions(superuser_only=False, permissions=(u'pylucid.change_pagecontent',))
@render_to("tools/highlight_code.html")
def highlight_code(request):
    """ hightlight sourcecode for copy&paste """
    context = {
        "title": _("hightlight sourcecode"),
        "form_url": request.path,
    }

    try:
        pygments_css = EditableHtmlHeadFile.on_site.get(filepath="pygments.css")
    except EditableHtmlHeadFile.DoesNotExist:
        request.page_msg("Error: No headfile with filepath 'pygments.css' found.")
    else:
        absolute_url = pygments_css.get_absolute_url(colorscheme=None)
        context["pygments_css"] = absolute_url

    if request.method == "POST":
        form = HighlightCodeForm(request.POST)
        if form.is_valid():
            sourcecode = form.cleaned_data["sourcecode"]
            source_type = form.cleaned_data["source_type"]

            highlighted = make_html(sourcecode, source_type)
            context["highlighted"] = highlighted

            html_code = make_html(highlighted, "html")
            context["html_code"] = html_code
    else:
        form = HighlightCodeForm()

    context["form"] = form
    return context
