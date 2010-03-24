# coding: utf-8

"""
    PyLucid update views
    ~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import re
import posixpath
from pprint import pformat

from django.conf import settings
from django.db import transaction
from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from django.template.loader import find_template_source
from django.contrib.redirects.models import Redirect
from django.template.defaultfilters import slugify

from dbtemplates.models import Template

from dbpreferences.models import Preference

from pylucid_project.utils.SimpleStringIO import SimpleStringIO
from pylucid_project.system.pylucid_plugins import PYLUCID_PLUGINS

from pylucid_project.apps.pylucid.fields import CSS_VALUE_RE
from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid.system.css_color_utils import filter_content, extract_colors
from pylucid_project.apps.pylucid.models import PageTree, PageMeta, PageContent, PluginPage, ColorScheme, Design, \
                                                EditableHtmlHeadFile, UserProfile, LogEntry, Language

from pylucid_project.apps.pylucid_update.models import Page08, Template08, Style08, JS_LoginData08
from pylucid_project.apps.pylucid_update.forms import UpdateForm, WipeSiteConfirm


def _get_output(request, out, title):
    """ prepare output, merge page_msg and create a LogEntry. """
    output = out.getlines()

    msg_list = request.page_msg.get_and_delete_messages()
    if msg_list:
        output.append("\nPage Messages:\n")
        for msg in msg_list:
            output += msg["lines"]
        request.page_msg.info("Page messages merge into the output.")

    LogEntry.objects.log_action(
        "pylucid_update", title, request, "successful", long_message="\n".join(output)
    )

    return output


def fix_old_user(out, obj, attrnames, alternative_user):
    """
    replace the old models.ForeignKey(User) with the current user, if the old user doesn't exist.
    """
    for attrname in attrnames:
        try:
            user_id = getattr(obj, attrname).id
        except User.DoesNotExist, err:
            out.write("Old %s user doesn't exist. Use current user %r." % (attrname, alternative_user))
            setattr(obj, attrname, alternative_user)



@check_permissions(superuser_only=True)
@render_to("pylucid_update/wipe_site.html")
def wipe_site(request):
    """ Delete all PageTree, PageMeta, PagePlugin for the current site. """
    current_site = Site.objects.get_current()
    title = _("Wipe all page data on '%s'." % current_site.name)
    context = {"title": title, "site": current_site}
    out = SimpleStringIO()

    if request.method == 'POST':
        form = WipeSiteConfirm(request.POST)
        if form.is_valid():

            sid = transaction.savepoint()
            try:
                Preference.objects.all().filter(site=current_site).delete()
                PageTree.on_site.all().delete()
            except Exception, err:
                transaction.savepoint_rollback(sid)
                import traceback
                LogEntry.objects.log_action("pylucid_update", title, request, "Error: %s" % err,
                    long_message=traceback.format_exc())
                raise
            else:
                transaction.savepoint_commit(sid)
                LogEntry.objects.log_action("pylucid_update", title, request, "successful")
                request.page_msg("Wipe site data successful")

            return HttpResponseRedirect(reverse("PyLucidUpdate-menu"))
    else:
        form = WipeSiteConfirm()

    context["form"] = form
    return context


@check_permissions(superuser_only=True)
@render_to("pylucid_update/menu.html")
def menu(request):
    """ Display a menu with all update view links """
    context = {
        "title": "PyLucid v0.8 migation - menu",
        "site": Site.objects.get_current(),
        "old_permalink_prefix": settings.PYLUCID.OLD_PERMALINK_PREFIX,
    }
    return context

def _cleanup_filename(filename):
    filename = filename.replace(" ", "_")
    return filename

def _make_new_template_name(template_name, site):
    return _cleanup_filename(
        posixpath.join(settings.SITE_TEMPLATE_PREFIX, slugify(site.name), template_name + ".html")
    )

def _make_new_style_name(style_name, site):
    return _cleanup_filename(
        posixpath.join(settings.SITE_STYLE_PREFIX, slugify(site.name), style_name + ".css")
    )


@check_permissions(superuser_only=True)
@render_to("pylucid_update/update08result.html")
def update08migrate_stj(request):
    out = SimpleStringIO()
    site = Site.objects.get_current()
    title = "migrate v0.8 styles, templates, JS-SHA-Login data (on site: %s)" % site

    out.write("Move JS-SHA-Login data into new UserProfile\n")
    for old_entry in JS_LoginData08.objects.all():
        try:
            user = old_entry.user
        except User.DoesNotExist, err:
            out.write("Old JS_LoginData08 User doesn't exist. Skip updating UserProfile.")
            continue

        userprofile, created = UserProfile.objects.get_or_create(user=user)
        if created:
            out.write("UserProfile for user '%s' created." % user.username)
        else:
            out.write("UserProfile for user '%s' exist." % user.username)

        if not userprofile.sha_login_checksum:
            # Add old sha login data, only if not exist.
            sha_login_checksum = old_entry.sha_checksum
            userprofile.sha_login_checksum = sha_login_checksum

            sha_login_salt = old_entry.salt
            userprofile.sha_login_salt = sha_login_salt

            userprofile.save()
            out.write("Add old JS-SHA-Login data.")

    out.write("\n______________________________________________________________")
    out.write("Move template model\n")
    for template in Template08.objects.all():
        new_template_name = _make_new_template_name(template.name, site)
        new_template, created = Template.objects.get_or_create(
            name=new_template_name,
            defaults={
                "content": template.content,
                "creation_date": template.createtime,
                "last_changed": template.lastupdatetime,
            }
        )
        new_template.save()
        new_template.sites.add(site)
        if created:
            out.write("template %r transferted to dbtemplate: %r" % (template.name, new_template_name))
        else:
            out.write("dbtemplate '%s' exist." % new_template_name)

    out.write("\n______________________________________________________________")
    out.write("Move style model\n")
    for style in Style08.objects.all():
        new_style_name = _make_new_style_name(style.name, site)
        new_staticfile, created = EditableHtmlHeadFile.objects.get_or_create(
            filepath=new_style_name,
            defaults={
                "description": style.description,
                "content": style.content,
                "createtime": style.createtime,
                "lastupdatetime": style.lastupdatetime,
            }
        )
        if created:
            out.write("stylesheet %r transferted into EditableStaticFile: %r" % (style.name, new_style_name))
        else:
            out.write("EditableStaticFile %r exist." % new_style_name)

    output = _get_output(request, out, title) # merge page_msg and log the complete output

    context = {
        "title": title,
        "site": site,
        "results": output,
    }
    return context


def _update08migrate_pages(request, language):
    """
    Mirgate page data from a old v0.8 installation into the new v0.9 tables.
    
    Originally, this migration can be callable multiple times. But we migrate the old tree not
    in hierarchical order. Thus, migration can only be called unique.
    """
    site = Site.objects.get_current()
    title = "migrate v0.8 pages (on site: %s)" % site
    out = SimpleStringIO()

    out.write("migrate old page model data")

    old_pages = Page08.objects.order_by('parent', 'id').all()

    designs = {}
    page_dict = {}
    parent_attach_data = {}
    new_page_id_data = {}
    for old_page in old_pages:
        out.write("\nmove '%s' page (old ID:%s)" % (old_page.name, old_page.id))

        fix_old_user(
            out, obj=old_page, attrnames=["createby", "lastupdateby"], alternative_user=request.user
        )

        #---------------------------------------------------------------------
        # create/get Design entry

        if old_page.template.name == old_page.style.name:
            design_key = "%s (v0.8 migration)" % (old_page.template.name)
        else:
            design_key = "%s + %s (v0.8 migration)" % (old_page.template.name, old_page.style.name)

        if design_key in designs:
            design = designs[design_key]
            out.write("Design: %r created in the past." % design)
        else:
            # The template/style combination was not created, yet.
            new_template_name = _make_new_template_name(old_page.template.name, site)
            design, created = Design.objects.get_or_create(
                name=design_key, defaults={"template": new_template_name}
            )
            if created:
                out.write("New design %s created." % design_key)
            else:
                out.write("Use existing Design: %r" % design)

            # Add old page css file            
            new_style_name = _make_new_style_name(old_page.style.name, site)
            try:
                css_file = EditableHtmlHeadFile.on_site.get(filepath=new_style_name)
            except EditableHtmlHeadFile.DoesNotExist:
                out.write("Error getting headfile %r. (Can't add it to design %r)" % (new_style_name, design))
            else:
                design.headfiles.add(css_file)

            colorscheme, created = ColorScheme.objects.get_or_create(name=old_page.style.name)
            if created:
                out.write("Use new color scheme: %s" % colorscheme.name)
                out.write("Colors can be extracted later.")
            else:
                out.write("Use color scheme: %s" % colorscheme.name)

            design.colorscheme = colorscheme
            design.save()
            designs[design_key] = design

        #---------------------------------------------------------------------
        # create PageTree entry

        page_parent_exist = True # Exist the parent page tree or was he not created, yet?
        if old_page.parent == None:
            parent = None
        else:
            old_parent_id = old_page.parent.id
            try:
                parent = page_dict[old_parent_id]
            except KeyError, err:
                page_parent_exist = False
                msg = (
                    " *** Error: parent id %r not found!"
                    " Attach as root page and try later."
                ) % old_parent_id
                out.write(msg)

        tree_entry = PageTree(
            site=site,
            slug=old_page.shortcut,
            parent=parent,
            position=old_page.position,
            page_type=PageTree.PAGE_TYPE, # FIXME: Find plugin entry in page content
            design=design,
            createtime=old_page.createtime,
            lastupdatetime=old_page.lastupdatetime,
            createby=old_page.createby,
            lastupdateby=old_page.lastupdateby,
        )
        tree_entry.save()
        out.write("PageTree entry '%s' created." % tree_entry.slug)

        # Collect the information old page ID <-> new PageTree ID
        new_page_id_data[old_page.id] = tree_entry.id

        page_dict[old_page.id] = tree_entry

        if old_page.id in parent_attach_data:
            # We have create a page tree witch was missing in the past.
            # Attach the right parent
            out.write(" +++ Attach the now created page tree %r as parent to:" % tree_entry)
            for created_page in parent_attach_data[old_page.id]:
                out.write("\t%r" % created_page)
                created_page.parent = tree_entry
                created_page.save()
            del(parent_attach_data[old_page.id]) # No longer needed

        if not page_parent_exist:
            # The parent page for the created tree_entry was not created yed.
            # Save this and attach the right parent page, after create.
            out.write("Remember page %r for later parent attach." % tree_entry)
            if old_parent_id not in parent_attach_data:
                parent_attach_data[old_parent_id] = [tree_entry]
            else:
                parent_attach_data[old_parent_id].append(tree_entry)

        #---------------------------------------------------------------------
        # create PageMeta entry

        pagemeta_entry = PageMeta(
            pagetree=tree_entry,
            language=language,
            name=old_page.name,
            title=old_page.title,
            keywords=old_page.keywords,
            description=old_page.description,

            # django-tagging can't handle case insensitive tags :(
            # So we get a duplicate entry IntegrityError an e.g.: "CGI, cgi"
            # work-a-round here: .lower() all tags :(
            # see: http://code.google.com/p/django-tagging/issues/detail?id=46
            tags=old_page.keywords.lower(),

            createtime=old_page.createtime,
            lastupdatetime=old_page.lastupdatetime,
            createby=old_page.createby,
            lastupdateby=old_page.lastupdateby,
        )
        pagemeta_entry.save()
        out.write("PageMeta entry '%s' - '%s' created." % (language, tree_entry.slug))

        #---------------------------------------------------------------------
        # create PageContent or PluginPage entry

        if old_page.content.strip() == "{% lucidTag blog %}":
            # Create a blog plugin page, but only if there is no additional content
            tree_entry.page_type = PageTree.PLUGIN_TYPE
            tree_entry.save()

            new_pluginpage = PluginPage(app_label="pylucid_project.pylucid_plugins.blog")
            new_pluginpage.pagetree = tree_entry
            new_pluginpage.save()
            out.write("PluginPage entry 'blog' created for: %r" % tree_entry)
        else:
            # create PageContent entry    
            content_entry = PageContent(
                pagemeta=pagemeta_entry,
                content=old_page.content,
                markup=old_page.markup,
                createtime=old_page.createtime,
                lastupdatetime=old_page.lastupdatetime,
                createby=old_page.createby,
                lastupdateby=old_page.lastupdateby,
            )
            content_entry.save()
            out.write("PageContent entry '%s' - '%s' created." % (language, tree_entry.slug))


    # Save the information old page ID <-> new PageTree ID, for later use in other views.
    LogEntry.objects.log_action(
        "pylucid_update", "v0.8 migation (site id: %s)" % site.id,
        request, "page id data", data=new_page_id_data,
    )
    output = _get_output(request, out, title) # merge page_msg and log the complete output

    context = {
        "template_name": "pylucid_update/update08result.html",
        "title": title,
        "site": site,
        "results": output,
    }
    return context


@render_to("pylucid_update/select_language.html")
def _select_lang(request, context, call_func):
    """
    Select language before start updating.
    """
    if Language.on_site.count() == 0:
        request.page_msg.error(_("Error: On this site exist no language!"))
        return HttpResponseRedirect(reverse("PyLucidUpdate-menu"))

    if request.method == 'POST':
        form = UpdateForm(request.POST)
        if form.is_valid():
            language = form.cleaned_data["language"]
            sid = transaction.savepoint()
            try:
                response = call_func(request, language)
            except Exception, err:
                transaction.savepoint_rollback(sid)
                import traceback
                LogEntry.objects.log_action("pylucid_update", context["title"], request, "Error: %s" % err,
                    long_message=traceback.format_exc())
                raise
            else:
                transaction.savepoint_commit(sid)
                LogEntry.objects.log_action("pylucid_update", context["title"], request, "successful")
            return response
    else:
        form = UpdateForm()

    context.update({
        "site": Site.objects.get_current(),
        "form": form,
    })
    return context



@check_permissions(superuser_only=True)
def update08migrate_pages(request):
    """
    Update PyLucid v0.8 model data to v0.9 models
    Before start updating, select the language.
    """
    if PageTree.on_site.count() != 0:
        request.page_msg(_("Can't start migrating: There exist pages on this side!"))
        request.page_msg(_("Create a new site or wipe all page data."))
        return HttpResponseRedirect(reverse("PyLucidUpdate-menu"))

    context = {
        "title": "Update PyLucid v0.8 model data to v0.9 models",
        "url": reverse("PyLucidUpdate-update08migrate_pages"),
    }
    return _select_lang(request, context, call_func=_update08migrate_pages)



def _get_page_id_data(site):
    """
    returns the dict with the information old page ID <-> new PageTree ID
    """
    return LogEntry.objects.filter(
        app_label="pylucid_update",
        action="v0.8 migation (site id: %s)" % site.id,
        message="page id data"
    ).order_by('-createtime')[0].data


def _replace(content, out, old, new):
    if old in content:
        out.write("replace %r with %r" % (old, new))
        content = content.replace(old, new)
    return content


OLD_PREMALINK_RE = re.compile("/%s/(\d+)/" % settings.PYLUCID.OLD_PERMALINK_PREFIX)
def _update_permalink(content, old_to_new_id):
    """ update old permalinks in page content """
    def update_permalink(m):
        old_id = int(m.group(1))
        if old_id in old_to_new_id:
            new_pagetree_id = old_to_new_id[old_id]
            return "/%s/%i/" % (
                settings.PYLUCID.PERMALINK_URL_PREFIX, new_pagetree_id
            )
        return m.group(0)

    new_content = OLD_PREMALINK_RE.sub(update_permalink, content)
    return new_content


@check_permissions(superuser_only=True)
@render_to("pylucid_update/update08result.html")
def update08pages(request):
    site = Site.objects.get_current()
    title = "Update %s PageContent" % site.name
    out = SimpleStringIO()

    # get the dict with the information old page ID <-> new PageTree ID
    new_page_id_data = _get_page_id_data(site)

    # Update only the PageContent objects from the current site.
    pages = PageContent.objects.filter(pagemeta__pagetree__site=site)
    count = 0
    delete_ids = []
    for pagecontent in pages:
        content = pagecontent.content

        content = _update_permalink(content, new_page_id_data)
        if content != pagecontent.content:
            out.write("Permalink in page %r updated." % pagecontent.get_absolute_url())

        if "{% lucidTag blog %}" in content:
            # There exist additional content in this page -> don't delete it 
            msg = (
                "*** You must manually convert page %s into a real blog plugin page!"
            ) % pagecontent.get_absolute_url()
            out.write(msg)

        content = _replace(content, out,
            "{% lucidTag page_update_list %}", "{% lucidTag update_journal %}"
        )
        content = _replace(content, out, "{% lucidTag RSS ", "{% lucidTag rss ")
        if content == pagecontent.content:
            # Nothing changed
            continue
        count += 1
        pagecontent.content = content
        pagecontent.save()
        out.write("PageContent updated: %r\n" % pagecontent)

    if delete_ids:
        out.write("Delete %s obsolete PageContent items: %r" % (len(delete_ids), delete_ids))
        PageContent.objects.filter(id__in=delete_ids).delete()

    out.write("\n%s PageContent items processed." % len(pages))
    out.write("%s items updated." % count)

    output = _get_output(request, out, title) # merge page_msg and log the complete output

    context = {
        "title": title,
        "site": site,
        "results": output,
    }
    return context



def _replace08URLs(request, language):
    """ replace old absolute page URLs with new permalink. """
    site = Site.objects.get_current()
    title = "Add %s permalink Redirect entries." % site.name
    out = SimpleStringIO()

    # get the dict with the information old page ID <-> new PageTree ID
    new_page_id_data = _get_page_id_data(site)

    old_pages = Page08.objects.only("id", "shortcut")
    old_absolute_urls = []
    url_to_new_id = {} # old absolute url <-> new PageTree ID
    too_short_urls = []
    for old_page in old_pages:
        old_absolute_url = old_page.get_absolute_url()
        if old_page.parent == None:
            too_short_urls.append(old_absolute_url)
        else:
            url_to_new_id[old_absolute_url] = new_page_id_data[old_page.id]
            old_absolute_urls.append(old_absolute_url)

    out.write("Skip too short urls: %r" % too_short_urls)

    # sort from longest to shortest
    old_absolute_urls.sort(cmp=lambda x, y: cmp(len(x), len(y)), reverse=True)

    # Update only the PageContent objects from the current site.
    pages = PageContent.objects.filter(pagemeta__pagetree__site=site)
    count = 0
    permalink_cache = {}
    replace_data = []
    for pagecontent in pages:
        content = pagecontent.content

        for old_absolute_url in old_absolute_urls:
            if old_absolute_url in content:
                if old_absolute_url in permalink_cache:
                    permalink = permalink_cache[old_absolute_url]
                else:
                    page_tree_id = url_to_new_id[old_absolute_url]
                    page_tree = PageTree.objects.get(id=page_tree_id)
                    page_meta = PageMeta.objects.get(pagetree=page_tree, language=language)
                    permalink = page_meta.get_permalink()
                    permalink_cache[old_absolute_url] = permalink

                page_absolute_url = pagecontent.get_absolute_url()

                content = content.replace(old_absolute_url, permalink)

                replace_data.append({
                    "old_absolute_url": old_absolute_url,
                    "permalink": permalink,
                    "page_absolute_url": page_absolute_url,
                })
                out.write("replace %r with %r in page %r" % (
                    old_absolute_url, permalink, page_absolute_url
                ))

        if content == pagecontent.content:
            # Nothing changed
            continue
        count += 1
        pagecontent.content = content
        pagecontent.save()
        out.write("PageContent updated: %r\n" % pagecontent)

    out.write("\n%s PageContent items processed." % len(pages))
    out.write("%s items updated." % count)

    output = _get_output(request, out, title) # merge page_msg and log the complete output

    context = {
        "template_name": "pylucid_update/replace08URLs.html",
        "title": title,
        "site": site,
        "too_short_urls": too_short_urls,
        "replace_data": replace_data,
        "items_count": len(pages),
        "update_count": count,
    }
    return context


@check_permissions(superuser_only=True)
def replace08URLs(request):
    """
    Update PyLucid v0.8 model data to v0.9 models
    Before start updating, select the language.
    """
    context = {
        "title": "Update old absolute urls in PageContent",
        "url": reverse("PyLucidUpdate-replace08URLs"),
    }
    return _select_lang(request, context, call_func=_replace08URLs)






@check_permissions(superuser_only=True)
@render_to("pylucid_update/update08result.html")
def update08pagesRedirect(request):
    site = Site.objects.get_current()
    title = "Add %s permalink Redirect entries." % site.name
    out = SimpleStringIO()

    new_page_id_data = _get_page_id_data(site)

    for (old_page_id, tree_entry_id) in new_page_id_data.iteritems():
        old_page = Page08.objects.only("id", "shortcut").get(id=old_page_id)

        old_path = "/%s/%i/%s/" % (settings.PYLUCID.OLD_PERMALINK_PREFIX, old_page.id, old_page.shortcut)
        new_path = "/%s/%i/%s/" % (settings.PYLUCID.PERMALINK_URL_PREFIX, tree_entry_id, old_page.shortcut)

        created = Redirect.objects.get_or_create(
            site=site, old_path=old_path,
            defaults={"new_path":new_path}
        )[1]
        if created:
            out.write("Add permalink redirect. ( %s -> %s )" % (old_path, new_path))
        else:
            out.write("Permalink redirect for this page exist. ( %s -> %s )" % (old_path, new_path))

    output = _get_output(request, out, title) # merge page_msg and log the complete output

    context = {
        "title": title,
        "site": site,
        "results": output,
    }
    return context


@check_permissions(superuser_only=True)
@render_to("pylucid_update/update08result.html")
def update08templates(request):
    site = Site.objects.get_current()
    title = "Update PyLucid v0.8 %s templates" % site.name
    out = SimpleStringIO()

    templates = Template.on_site.filter(name__istartswith=settings.SITE_TEMPLATE_PREFIX)

    count = 0
    for template in templates:
        out.write("\n______________________________________________________________")
        out.write("Update Template: '%s'\n" % template.name)

        content = template.content

        SCRIPT_TAG = (
            '<script src="%(url)s"'
            ' onerror="JavaScript:alert(\'Error loading file [%(url)s] !\');"'
            ' type="text/javascript" /></script>\n'
        )

        new_head_file_tag = ""
        new_head_file_tag += SCRIPT_TAG % {
            "url": posixpath.join(settings.MEDIA_URL, settings.PYLUCID.PYLUCID_MEDIA_DIR, "jquery.js")
        }
        new_head_file_tag += SCRIPT_TAG % {
            "url": posixpath.join(
                settings.MEDIA_URL, settings.PYLUCID.PYLUCID_MEDIA_DIR, "pylucid_js_tools.js"
            )
        }
        new_head_file_tag += '<!-- ContextMiddleware extrahead -->\n'

        content = _replace(content, out, "{% lucidTag page_style %}", new_head_file_tag)
        # temp in developer version:
        content = _replace(content, out, "{% lucidTag head_files %}", new_head_file_tag)
        content = _replace(content, out, "<!-- ContextMiddleware head_files -->", new_head_file_tag)

        content = _replace(content, out, "{{ login_link }}", "{% lucidTag auth %}")

        content = _replace(content, out, "{% lucidTag back_links %}", "<!-- ContextMiddleware breadcrumb -->")
        content = _replace(content, out,
            "{{ PAGE.content }}",
            '<div id="page_content">\n'
            '    {% block content %}{{ page_content }}{% endblock content %}\n'
            '</div>'
        )
        content = _replace(content, out, "{{ PAGE.get_permalink }}", "{{ page_permalink }}")
        content = _replace(content, out, "{{ page_get_permalink }}", "{{ page_permalink }}") # dev version only
        content = _replace(content, out,
            "{% if PAGE.title %}{{ PAGE.title|escape }}{% else %}{{ PAGE.name|escape }}{% endif %}",
            "{{ page_title }}"
        )
        content = _replace(content, out, "PAGE.title", "page_title")
        content = _replace(content, out, "{{ PAGE.keywords }}", "{{ page_keywords }}")
        content = _replace(content, out, "{{ PAGE.description }}", "{{ page_description }}")
        content = _replace(content, out, "{{ robots }}", "{{ page_robots }}")

        content = _replace(content, out, "{{ PAGE.datetime", "{{ page_createtime")

        for timestring in ("lastupdatetime", "createtime"):
            # Change time with filter:
            content = _replace(content, out,
                "{{ PAGE.%s" % timestring,
                "{{ page_%s" % timestring
            )
            # add i18n filter, if not exist:
            content = _replace(content, out,
                "{{ page_%s }}" % timestring,
                '{{ page_%s|date:_("DATETIME_FORMAT") }}' % timestring,
            )

        content = _replace(content, out, "{{ PAGE.", "{{ page_")

        content = _replace(content, out, "{% lucidTag RSS ", "{% lucidTag rss ")

        if "{% lucidTag language %}" not in content:
            # Add language plugin after breadcrumb, if not exist
            content = _replace(content, out,
                "<!-- ContextMiddleware breadcrumb -->",
                "<!-- ContextMiddleware breadcrumb -->\n"
                "<p>{% lucidTag language %}</p>\n"
            )

        # TODO: add somthing like: <meta http-equiv="Content-Language" content="en" />

        if "<!-- page_messages -->" not in content:
            out.write(" *** IMPORTANT: You must insert <!-- page_messages --> in this template!")

        if template.content == content:
            out.write("Nothing changed")
        else:
            template.content = content
            template.save()
            count += 1
            out.write("Template updated.")

    out.write("\n\n%s Template items processed." % len(templates))
    out.write("%s items updated." % count)

    output = out.getlines()
    LogEntry.objects.log_action(
        "pylucid_update", title, request, "successful", long_message="\n".join(output)
    )

    context = {
        "title": title,
        "site": site,
        "results": output,
    }
    return context



@check_permissions(superuser_only=True)
@render_to("pylucid_update/update08result.html")
def update08styles(request):
    """
    TODO: We should not add any styles... We should create a new EditableHtmlHeadFile stylesheet
    file and add this to all Design!
    """
    site = Site.objects.get_current()
    title = "Update PyLucid v0.8 %s styles" % site.name
    out = SimpleStringIO()

    def update_headfile_colorscheme(design, headfile):
        out.write("\nExtract colors from: '%s'" % headfile.filepath)

        colorscheme = design.colorscheme
        if colorscheme == None:
            # This design has no color scheme, yet -> create one
            colorscheme = ColorScheme(name=headfile.filepath)
            colorscheme.save()
            out.write("Add color scheme %r to %r" % (colorscheme.name, design.name))
            design.colorscheme = colorscheme
            design.save()

        out.write("Use color scheme %r" % colorscheme.name)

        content = headfile.content
        new_content, color_dict = extract_colors(content)
        out.write(repr(new_content))
        out.write(pformat(color_dict))

        try:
            created, updated, exists = colorscheme.update(color_dict)
        except ValidationError, err:
            out.write("Error updating colorscheme: %s" % err)
            return

        out.write("created %s colors: %r" % (len(created), created))
        out.write("updated %s colors: %r" % (len(updated), updated))
        out.write("exists %s colors: %r" % (len(exists), exists))

        colorscheme.save()

        headfile.content = new_content
        headfile.render = True
        headfile.save()


    def update_all_design_colorscheme(design):
        headfiles = design.headfiles.all()
        out.write("\nExisting headfiles: %r" % headfiles)

        for headfile in headfiles:
            if not headfile.filepath.lower().endswith(".css"):
                out.write("Skip headfile: %r" % headfile)
            else:
                update_headfile_colorscheme(design, headfile)

    designs = Design.on_site.all()
    for design in designs:
        out.write("\n______________________________________________________________")
        out.write("\nUpdate color scheme for design: '%s'" % design.name)

        update_all_design_colorscheme(design)


#    styles = EditableHtmlHeadFile.objects.filter(filepath__istartswith=settings.SITE_TEMPLATE_PREFIX)
#    styles = styles.filter(filepath__iendswith=".css")
#    for style in styles:
#        out.write("\n______________________________________________________________")
#        out.write("\nUpdate Style: '%s'" % style.filepath)
#        
#        content = style.content
#        filtered_content = filter_content(content) # Skip all pygments styles
#        out.write(filtered_content)
#        
#        new_content, color_dict = extract_colors(content)
#        out.write(new_content)
#        out.write(repr(color_dict))

#    def replace(content, out, old, new):
#        out.write("replace %r with %r" % (old, new))
#        if not old in content:
#            out.write("String not found. Updated already?")
#        else:
#            content = content.replace(old, new)
#        return content
#    
#    # Get the file content via django template loader:
#    additional_styles, origin = find_template_source("pylucid_update/additional_styles.css")
#        
#    styles = EditableHtmlHeadFile.objects.filter(filepath__istartswith=settings.SITE_TEMPLATE_PREFIX)
#    styles = styles.filter(filepath__iendswith=".css")
#    for style in styles:
#        out.write("\n______________________________________________________________")
#        out.write("\nUpdate Style: '%s'" % style.filepath)
#        
#        content = style.content
#        if additional_styles in content:
#            out.write("additional styles allready inserted.")
#        else:
#            content = additional_styles + content
#            style.content = content
#            style.save()
#            out.write("additional styles inserted.")        

    output = out.getlines()
    LogEntry.objects.log_action(
        "pylucid_update", title, request, "successful", long_message="\n".join(output)
    )

    context = {
        "title": title,
        "site": site,
        "results": output,
    }
    return context


@check_permissions(superuser_only=True)
def update08plugins(request):
    """
    Update PyLucid v0.8 model data to v0.9 models
    Before start updating, select the language.
    """
    context = {
        "template_name": "pylucid_update/update08plugins.html",
        "title": "Update PyLucid v0.8 plugin data",
        "url": reverse("PyLucidUpdate-update08plugins"),
    }
    return _select_lang(request, context, call_func=_update08plugins)




def _update08plugins(request, language):
    site = Site.objects.get_current()
    title = "Update PyLucid v0.8 plugin data"
    out = SimpleStringIO()

    method_kwargs = {
        "out": out,
        "language": language,
    }

    filename = settings.PYLUCID.UPDATE08_PLUGIN_FILENAME
    view_name = settings.PYLUCID.UPDATE08_PLUGIN_VIEWNAME

    for plugin_name, plugin_instance in PYLUCID_PLUGINS.iteritems():
        try:
            plugin_instance.call_plugin_view(request, filename, view_name, method_kwargs)
        except Exception, err:
            if str(err).endswith("No module named %s" % filename):
                # Plugin has no update API
                continue
            if settings.DEBUG:
                raise
            request.page_msg.error("failed updating %s." % plugin_name)
            request.page_msg.insert_traceback()
        else:
            out.write(" --- %s END ---" % plugin_name)

    output = out.getlines()
    LogEntry.objects.log_action(
        "pylucid_update", title, request, "successful", long_message="\n".join(output)
    )

    context = {
        "template_name": "pylucid_update/update08result.html",
        "title": title,
        "site": site,
        "results": output,
    }
    return context
