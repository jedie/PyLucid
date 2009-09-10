# coding:utf-8

from django import http
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from pylucid.decorators import check_permissions, render_to
from pylucid.markup.converter import apply_markup

from pylucid_admin.admin_menu import AdminMenu

from blog.forms import BlogEntryForm



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
    user_profile = request.user.get_profile()
    # All accessible sites from the current user:
    user_site_ids = user_profile.sites.values_list("id", "name")
    m2m_limit = {"sites": user_site_ids} # Limit the site choice field with LimitManyToManyFields

    context = {
        "title": _("Create a new blog entry"),
        "form_url": request.path,
    }

    if request.method == "POST":
        form = BlogEntryForm(m2m_limit, request.POST)
        if form.is_valid():
            if "preview" in request.POST:
                context["preview"] = apply_markup(
                    form.cleaned_data["content"], form.cleaned_data["markup"],
                    request.page_msg, escape_django_tags=True
                )
            else:
                instance = form.save()
                request.page_msg(_("New blog entry '%s' saved.") % instance.headline)
                return http.HttpResponseRedirect(instance.get_absolute_url())
    else:
        initial = {
            "sites": [Site.objects.get_current().pk], # preselect current site
            "language": request.PYLUCID.language_entry.pk, # preselect current language
        }
        form = BlogEntryForm(m2m_limit, initial=initial)

    context["form"] = form
    return context

