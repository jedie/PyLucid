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

from django.conf import settings
from django.db import transaction
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response
from django.template.loader import find_template_source

from dbtemplates.models import Template

from pylucid_project.utils.SimpleStringIO import SimpleStringIO
from pylucid.models import PageTree, PageMeta, PageContent, ColorScheme, Design, EditableHtmlHeadFile, \
                                                                                            UserProfile
from pylucid_project.apps.pylucid_update.models import Page08, Template08, Style08, JS_LoginData08
from pylucid.system.css_color_utils import filter_content, extract_colors
from pylucid_project.apps.pylucid_update.forms import UpdateForm
from pylucid.fields import CSS_VALUE_RE


def menu(request):
    """ Display a menu with all update view links """
    context = {
        "title": "menu",
        "site": Site.objects.get_current()
    }
    return render_to_response('pylucid_update/menu.html', context, context_instance=RequestContext(request))


def _do_update(request, language):
    out = SimpleStringIO()
    site = Site.objects.get_current()
    out.write("Starting update and move v0.8 data into v0.9 (on site: %s)" % site)

    out.write("\n______________________________________________________________")
    out.write("Move JS-SHA-Login data into new UserProfile\n")
    for old_entry in JS_LoginData08.objects.all():
        user = old_entry.user
        sha_login_checksum = old_entry.sha_checksum
        sha_login_salt = old_entry.salt

        userprofile, created = UserProfile.objects.get_or_create(user=user)
        #userprofile.site.add(site)           
        if created:
            out.write("UserProfile for user '%s' created." % user.username)
        else:
            out.write("UserProfile for user '%s' exist." % user.username)

        if not userprofile.sha_login_checksum:
            # Add old sha login data, only if not exist.
            userprofile.sha_login_checksum = sha_login_checksum
            userprofile.sha_login_salt = sha_login_salt
            userprofile.save()
            out.write("Add old JS-SHA-Login data.")

    out.write("\n______________________________________________________________")
    out.write("Move template model\n")
    templates = {}
    for template in Template08.objects.all():
        new_template_name = settings.SITE_TEMPLATE_PREFIX + template.name + ".html"
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
        templates[template.name] = new_template_name
        if created:
            out.write("template '%s' transferted into dbtemplates." % template.name)
        else:
            out.write("dbtemplate '%s' exist." % template.name)

    out.write("\n______________________________________________________________")
    out.write("Move style model\n")
    cssfiles = {}
    for style in Style08.objects.all():
        new_staticfile, created = EditableHtmlHeadFile.objects.get_or_create(
            filepath=settings.SITE_TEMPLATE_PREFIX + style.name + ".css",
            defaults={
                "description": style.description,
                "content": style.content,
                "createtime": style.createtime,
                "lastupdatetime": style.lastupdatetime,
            }
        )
        cssfiles[style.name] = new_staticfile
        if created:
            out.write("stylesheet '%s' transferted into EditableStaticFile." % style.name)
        else:
            out.write("EditableStaticFile '%s' exist." % style.name)


    out.write("\n______________________________________________________________")
    out.write("migrate old page model data")

    old_pages = Page08.objects.order_by('parent', 'id').all()

    designs = {}
    page_dict = {}
    for old_page in old_pages:
        out.write("\nmove '%s' page (old ID:%s)" % (old_page.name, old_page.id))

        #---------------------------------------------------------------------
        # create/get Design entry

        design_key = "%s %s" % (old_page.template.name, old_page.style.name)
        if design_key not in designs:
            style_name = old_page.style.name
            # The template/style combination was not created, yet.
            if old_page.template.name == style_name:
                new_design_name = old_page.template.name
            else:
                new_design_name = "%s + %s" % (old_page.template.name, style_name)

            design, created = Design.objects.get_or_create(
                name=new_design_name,
                defaults={
                    "template": templates[old_page.template.name],
                }
            )
            if created:
                out.write("New design created: %s" % new_design_name)
            else:
                out.write("Use existing Design: %r" % design)

            # Add old page css file
            css_file = cssfiles[style_name] # EditableHtmlHeadFile instance
            assert isinstance(css_file, EditableHtmlHeadFile)
            design.headfiles.add(css_file)

            colorscheme, created = ColorScheme.objects.get_or_create(name=style_name)
            if created:
                out.write("Use new color scheme: %s" % colorscheme.name)
                out.write("Colors can be extracted later.")
            else:
                out.write("Use color scheme: %s" % colorscheme.name)

            design.colorscheme = colorscheme
            design.save()
            designs[design_key] = design
        else:
            design = designs[design_key]
            out.write("Use existing Design: %r" % design)

        #---------------------------------------------------------------------
        # create/get PageTree entry

        if old_page.parent == None:
            parent = None
        else:
            parent = page_dict[old_page.parent.id]

        tree_entry, created = PageTree.objects.get_or_create(
            site=site,
            slug=old_page.shortcut,
            parent=parent,
            defaults={
                "position": old_page.position,

                "type": PageTree.PAGE_TYPE, # FIXME: Find plugin entry in page content

                "design": design,

                "createtime": old_page.createtime,
                "lastupdatetime": old_page.lastupdatetime,
                "createby": old_page.createby,
                "lastupdateby": old_page.lastupdateby,
            }
        )
        if created:
            tree_entry.save()
            out.write("PageTree entry '%s' created." % tree_entry.slug)
        else:
            out.write("PageTree entry '%s' exist." % tree_entry.slug)

        page_dict[old_page.id] = tree_entry

        #---------------------------------------------------------------------
        # create/get PageMeta entry

        pagemeta_entry, created = PageMeta.objects.get_or_create(
            page=tree_entry,
            lang=language,
            defaults={
                "name": old_page.name,
                "title": old_page.title,
                "keywords": old_page.keywords,
                "description": old_page.description,

                "createtime": old_page.createtime,
                "lastupdatetime": old_page.lastupdatetime,
                "createby": old_page.createby,
                "lastupdateby": old_page.lastupdateby,
            }
        )
        if created:
            pagemeta_entry.save()
            out.write("PageMeta entry '%s' - '%s' created." % (language, tree_entry.slug))
        else:
            out.write("PageMeta entry '%s' - '%s' exist." % (language, tree_entry.slug))

        #---------------------------------------------------------------------
        # create/get PageContent entry

        content_entry, created = PageContent.objects.get_or_create(
            page=tree_entry,
            lang=language,
            pagemeta=pagemeta_entry,
            defaults={
                "content": old_page.content,
                "markup": old_page.markup,

                "createtime": old_page.createtime,
                "lastupdatetime": old_page.lastupdatetime,
                "createby": old_page.createby,
                "lastupdateby": old_page.lastupdateby,
            }
        )
        if created:
            content_entry.save()
            out.write("PageContent entry '%s' - '%s' created." % (language, tree_entry.slug))
        else:
            out.write("PageContent entry '%s' - '%s' exist." % (language, tree_entry.slug))

    context = {
        "title": "update data from PyLucid v0.8 to v0.9",
        "results": out.getlines(),
    }
    return render_to_response('pylucid_update/update08result.html', context,
        context_instance=RequestContext(request))


def update08(request):
    """ Update PyLucid v0.8 model data to v0.9 models """
    if request.method == 'POST':
        form = UpdateForm(request.POST)
        if form.is_valid():
            language = form.cleaned_data["language"]
            sid = transaction.savepoint()
            try:
                response = _do_update(request, language)
            except:# IntegrityError, e:
                transaction.savepoint_rollback(sid)
                raise
            else:
                transaction.savepoint_commit(sid)
                return response
    else:
        form = UpdateForm()

    context = {
        "title": "update data from PyLucid v0.8 to v0.9",
        "url": reverse("PyLucidUpdate-update08"),
        "site": Site.objects.get_current(),
        "form": form,
    }
    return render_to_response('pylucid_update/update08.html', context,
        context_instance=RequestContext(request))


def update08templates(request):
    title = "Update PyLucid v0.8 templates"
    out = SimpleStringIO()

    def replace(content, out, old, new):
        out.write("replace %r with %r" % (old, new))
        if not old in content:
            out.write("Source string not found, ok.")
        else:
            content = content.replace(old, new)
        return content


    for template in Template.objects.filter(name__istartswith=settings.SITE_TEMPLATE_PREFIX):
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

        content = replace(content, out, "{% lucidTag page_style %}", new_head_file_tag)
        # temp in developer version:
        content = replace(content, out, "{% lucidTag head_files %}", new_head_file_tag)
        content = replace(content, out, "<!-- ContextMiddleware head_files -->", new_head_file_tag)

        content = replace(content, out, "{{ login_link }}", "{% lucidTag auth %}")

        content = replace(content, out, "{% lucidTag back_links %}", "<!-- ContextMiddleware breadcrumb -->")
        content = replace(content, out,
            "{{ PAGE.content }}",
            '<div id="page_content">\n'
            '    {% block content %}{{ page_content }}{% endblock content %}\n'
            '</div>'
        )
        content = replace(content, out,
            "{% if PAGE.title %}{{ PAGE.title|escape }}{% else %}{{ PAGE.name|escape }}{% endif %}",
            "{{ page_title }}"
        )
        content = replace(content, out, "PAGE.title", "page_title")
        content = replace(content, out, "{{ PAGE.keywords }}", "{{ page_keywords }}")
        content = replace(content, out, "{{ PAGE.description }}", "{{ page_description }}")
        content = replace(content, out, "{{ robots }}", "{{ page_robots }}")

        content = replace(content, out, "{{ PAGE.datetime", "{{ page_createtime")

        for timestring in ("lastupdatetime", "createtime"):
            # Change time with filter:
            content = replace(content, out,
                "{{ PAGE.%s" % timestring,
                "{{ page_%s" % timestring
            )
            # add i18n filter, if not exist:
            content = replace(content, out,
                "{{ page_%s }}" % timestring,
                '{{ page_%s|date:_("DATETIME_FORMAT") }}' % timestring,
            )

        content = replace(content, out, "{{ PAGE.", "{{ page_")

        if "{% lucidTag language %}" not in content:
            # Add language plugin after breadcrumb, if not exist
            content = replace(content, out,
                "<!-- ContextMiddleware breadcrumb -->",
                "<!-- ContextMiddleware breadcrumb -->\n"
                "<p>{% lucidTag language %}</p>\n"
            )

        # TODO: add somthing like: <meta http-equiv="Content-Language" content="en" />

        template.content = content
        template.save()

        out.write("Template updated.")

    context = {
        "title": title,
        "results": out.getlines(),
    }
    return render_to_response('pylucid_update/update08result.html', context,
        context_instance=RequestContext(request))




def update08styles(request):
    """
    TODO: We should not add any styles... We should create a new EditableHtmlHeadFile stylesheet
    file and add this to all Design!
    """
    title = "Update PyLucid v0.8 styles"
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
        out.write(repr(color_dict))

        created, updated, exists = colorscheme.update(color_dict)
        out.write("created colors: %r" % created)
        out.write("updated colors: %r" % updated)
        out.write("exists colors: %r" % exists)

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

    for design in Design.objects.all():
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

    context = {
        "title": title,
        "results": out.getlines(),
    }
    return render_to_response('pylucid_update/update08result.html', context,
        context_instance=RequestContext(request))
