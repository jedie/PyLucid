# coding: utf-8

"""
    PyLucid blog plugin
    ~~~~~~~~~~~~~~~~~~~

    :copyleft: 2008-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""


from django import http
from django.contrib import messages
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid.markup.converter import apply_markup
from pylucid_project.apps.pylucid_admin.admin_menu import AdminMenu
from pylucid_project.utils.site_utils import get_site_preselection

from pylucid_project.pylucid_plugins.blog.models import BlogEntry, \
    BlogEntryContent
from pylucid_project.pylucid_plugins.blog.forms import BlogForm
from pylucid_project.pylucid_plugins.blog.preference_forms import BlogPrefForm




def install(request):
    """ insert PyLucid admin views into PageTree """
    output = []

    admin_menu = AdminMenu(request, output)
    menu_section_entry = admin_menu.get_or_create_section("create content")

    admin_menu.add_menu_entry(
        parent=menu_section_entry, url_name="Blog-new_blog_entry",
        name="new blog entry", title="Create a new blog entry.",
    )

    return "\n".join(output)


@check_permissions(superuser_only=False, permissions=("blog.add_blogentry",))
@render_to("blog/new_blog_entry.html")
def new_blog_entry(request):
    """
    TODO: Use Ajax in preview
    """
#    user_profile = request.user.get_profile()
    # All accessible sites from the current user:
#    user_site_ids = user_profile.sites.values_list("id", "name")
#    m2m_limit = {"sites": user_site_ids} # Limit the site choice field with LimitManyToManyFields

    context = {
        "title": _("Create a new blog entry"),
        "form_url": request.path,
        "tag_cloud": BlogEntryContent.objects.get_tag_cloud(request),
        "add_tag_filter_link": False, # Don't add filters in tag cloud
    }

    if request.method == "POST":
        form = BlogForm(request.POST)
        if form.is_valid():
            new_entry = BlogEntry.objects.create()
            new_entry.sites = form.cleaned_data["sites"]
            new_entry.save()

            blog_content = form.save(commit=False)
            blog_content.entry = new_entry
            blog_content.save()

            messages.success(request, _("New blog entry '%s' saved.") % blog_content.headline)
            return http.HttpResponseRedirect(blog_content.get_absolute_url())
    else:
        # Get preferences
        pref_form = BlogPrefForm()

        initial = {
            "sites": get_site_preselection(pref_form, request), # preselect sites field
            "language": request.PYLUCID.current_language.pk, # preselect current language
        }
        form = BlogForm(initial=initial)

    context["form"] = form
    return context

