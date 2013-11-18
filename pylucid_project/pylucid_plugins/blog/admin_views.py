# coding: utf-8

"""
    PyLucid blog plugin
    ~~~~~~~~~~~~~~~~~~~

    :copyleft: 2008-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""


from django import http, forms
from django.contrib import messages
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid.markup.converter import apply_markup
from pylucid_project.apps.pylucid_admin.admin_menu import AdminMenu
from pylucid_project.utils.site_utils import get_site_preselection

from pylucid_project.pylucid_plugins.blog.models import BlogEntry, \
    BlogEntryContent
from pylucid_project.pylucid_plugins.blog.forms import BlogForm, BlogContentForm
from pylucid_project.pylucid_plugins.blog.preference_forms import BlogPrefForm
from pylucid_project.apps.pylucid.models.language import Language
from pylucid_project.apps.i18n.views import select_language
# from pylucid_project.apps.i18n.utils.translate import prefill
from pylucid_project.apps.pylucid.models.pluginpage import PluginPage




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

    try:
        plugin_page = PluginPage.objects.filter(app_label__endswith="blog")[0]
    except IndexError:
        messages.error(request, _("There exist no blog plugin page, yet. Please create one, first."))
        return http.HttpResponseRedirect("/")

    context = {
        "title": _("Create a new blog entry"),
        "form_url": request.path,
        "tag_cloud": BlogEntryContent.objects.get_tag_cloud(request),
        "add_tag_filter_link": False,  # Don't add filters in tag cloud
    }

    if request.method == "POST":
        if "cancel" in request.POST:
            messages.info(request, _("Create new blog entry aborted, ok."))
            url = plugin_page.get_absolute_url()
            return http.HttpResponseRedirect(url)

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
            "sites": get_site_preselection(pref_form, request),  # preselect sites field
            "language": request.PYLUCID.current_language.pk,  # preselect current language
        }
        form = BlogForm(initial=initial)

    context["form"] = form
    return context


@check_permissions(superuser_only=False, permissions=("blog.change_blogentry",))
@render_to("blog/edit_blog_entry.html")
def edit_blog_entry(request, id=None):
    if id is None:
        raise

    entry = BlogEntryContent.objects.get(pk=id)
    if request.method == "POST":
        if "cancel" in request.POST:
            messages.info(request, _("Edit blog entry aborted, ok."))
            url = entry.get_absolute_url()
            return http.HttpResponseRedirect(url)

        form = BlogContentForm(request.POST, instance=entry)
        if form.is_valid():
            instance = form.save()
            messages.success(request, "%r updated." % instance)
            return http.HttpResponseRedirect(instance.get_absolute_url())
    else:
        form = BlogContentForm(instance=entry)

    return {
        "title": _("Edit a blog entry"),
        "form": form,
    }


@check_permissions(superuser_only=False, permissions=("blog.change_blogentry",))
@render_to()
def translate_blog_entry(request, id=None):
    if id is None:
        raise

    source_entry = BlogEntryContent.objects.get(pk=id)
    absolute_url = source_entry.get_absolute_url()

    # select the destination language
    result = select_language(request, absolute_url, source_entry.language, source_entry.headline)
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
        raise RuntimeError()  # Should never happen


    context = {
        "title": _("Translate a blog entry"),
        "template_name": "blog/translate_blog_entry.html",
        "abort_url": absolute_url,
    }

    try:
        dest_entry = BlogEntryContent.objects.get(entry=source_entry.entry, language=dest_language)
    except BlogEntryContent.DoesNotExist:
        dest_entry = None
        dest_initial = {
            "entry": source_entry.entry,
            "language":dest_language,
            "markup": source_entry.markup,
            "is_public": source_entry.is_public,
        }

    if request.method == "POST":
        source_form = BlogContentForm(request.POST, prefix="source", instance=source_entry)

        if dest_entry is None:
            dest_form = BlogContentForm(request.POST, prefix="dest", initial=dest_initial)
        else:
            dest_form = BlogContentForm(request.POST, prefix="dest", instance=dest_entry)

        if "autotranslate" in request.POST:
            raise NotImplementedError("TODO: Must be reimplemented!")
#             if source_form.is_valid():
#                 dest_form, filled_fields, errors = prefill(
#                     source_form, dest_form,
#                     source_entry.language, dest_language,
#                     only_fields=("headline", "content"),
#                     #debug=True,
#                 )
#                 if filled_fields:
#                     messages.success(request, "These fields are translated with google: %s" % ", ".join(filled_fields))
#                 else:
#                     messages.info(request, "No fields translated with google, because all fields have been a translation.")
#                 if errors:
#                     for error in errors:
#                         messages.error(request, error)
        else:
            if source_form.is_valid() and dest_form.is_valid():
                # All forms are valid -> Save all.
                source_form.save()
                dest_entry2 = dest_form.save(commit=False)
                dest_entry2.entry = source_entry.entry
                dest_entry2.save()
                if dest_entry is None:
                    messages.success(request, "All saved. New entry %r created." % dest_entry2)
                else:
                    messages.success(request, "All saved.")
                return http.HttpResponseRedirect(dest_entry2.get_absolute_url())
    else:
        source_form = BlogContentForm(prefix="source", instance=source_entry)
        if dest_entry is None:
            dest_form = BlogContentForm(prefix="dest", initial=dest_initial)
        else:
            dest_form = BlogContentForm(prefix="dest", instance=dest_entry)

    source_fields = []
    dest_fields = []
    line_fields = []
    for source_field, dest_field in zip(source_form, dest_form):
        assert source_field.name == dest_field.name
        if source_field.name in ("content", "language", "markup"):
            # Fields witch displayed side by side.
            source_fields.append(source_field)
            dest_fields.append(dest_field)
        else:
            # Fields witch renders alternating one below the other.
            source_field.language = source_entry.language
            line_fields.append(source_field)
            dest_field.language = dest_language
            line_fields.append(dest_field)

    if source_form.errors or dest_form.errors:
        has_errors = True
    else:
        has_errors = False

    context.update({
        "source_entry": source_entry,
        "dest_language": dest_language,
        "source_form": source_form,
        "dest_form": dest_form,
        "all_forms": [source_form, dest_form],
        "has_errors": has_errors,
        "source_fields": source_fields,
        "dest_fields": dest_fields,
        "line_fields": line_fields,
    })
    return context
