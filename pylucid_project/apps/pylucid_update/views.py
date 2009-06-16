# coding: utf-8

import posixpath

from django.conf import settings
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.loader import find_template_source
from django.contrib.auth.decorators import login_required

from dbtemplates.models import Template

from pylucid_project.utils.SimpleStringIO import SimpleStringIO
from pylucid_project.apps.pylucid.models import PageTree, PageMeta, PageContent, Design, \
                                                            EditableHtmlHeadFile, UserProfile
from pylucid_project.apps.pylucid_update.models import Page08, Template08, Style08, JS_LoginData08
from pylucid_project.apps.pylucid_update.forms import UpdateForm



@login_required
def menu(request):
    """ Display a menu with all update view links """
    context = {
        "title": "menu",
    }
    return render_to_response('pylucid_update/menu.html', context, context_instance=RequestContext(request))





def _do_update(request, site, language):
    out = SimpleStringIO()
    out.write("Starting update and move v0.8 data into v0.9 (on site: %s)" % site)

    #---------------------------------------------------------------------
    out.write("Move JS-SHA-Login data into new UserProfile")
    for old_entry in JS_LoginData08.objects.all():       
        user = old_entry.user
        sha_login_checksum = old_entry.sha_checksum
        sha_login_salt = old_entry.salt
        
        userprofile, created = UserProfile.objects.get_or_create(request,
            user = user,
            defaults = {
                "sha_login_checksum": sha_login_checksum,
                "sha_login_salt": sha_login_salt,
            }
        )
        userprofile.site.add(site)
        if created:
            out.write("UserProfile for user '%s' created." % user.username)
        else:
            out.write("UserProfile for user '%s' exist." % user.username)

    #---------------------------------------------------------------------
    out.write("Move template model")
    templates = {}
    for template in Template08.objects.all():
        new_template_name = settings.SITE_TEMPLATE_PREFIX + template.name + ".html"
        new_template, created = Template.objects.get_or_create(
            name = new_template_name,
            defaults = {
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

    #---------------------------------------------------------------------
    out.write("Move style model")
    cssfiles = {}
    for style in Style08.objects.all():
        new_staticfile, created = EditableHtmlHeadFile.objects.get_or_create(request,
            filepath = settings.SITE_TEMPLATE_PREFIX + style.name + ".css",
            defaults = {
                "description": style.description,
                "content": style.content,
                "createtime": style.createtime,
                "lastupdatetime": style.lastupdatetime,
            }
        )
        new_staticfile.site.add(site)
        cssfiles[style.name] = new_staticfile
        if created:
            out.write("stylesheet '%s' transferted into EditableStaticFile." % style.name)
        else:
            out.write("EditableStaticFile '%s' exist." % style.name)


    #---------------------------------------------------------------------
    # migrate old page model data

    old_pages = Page08.objects.order_by('parent', 'id').all()

    designs = {}
    page_dict = {}
    for old_page in old_pages:
        out.write("\nmove '%s' page (old ID:%s)" % (old_page.name, old_page.id))

        #---------------------------------------------------------------------
        # create/get Design entry
        
        design_key = "%s %s" % (old_page.template.name, old_page.style.name)
        if design_key not in designs:
            # The template/style combination was not created, yet.
            if old_page.template.name == old_page.style.name:
                new_design_name = old_page.template.name
            else:
                new_design_name = "%s + %s" % (old_page.template.name, old_page.style.name)
                
            design, created = Design.objects.get_or_create(request,
                name = new_design_name,
                defaults = {
                    "template": templates[old_page.template.name],
                }
            )
            design.site.add(site)
            if created:
                # Add old page css file
                design.headfiles.add(cssfiles[old_page.style.name])
                out.write("New design created: %s" % new_design_name)
            
            designs[design_key] = design
        else:
            design = designs[design_key]
            
        #---------------------------------------------------------------------
        # create/get PageTree entry

        if old_page.parent == None:
            parent = None
        else:
            parent = page_dict[old_page.parent.id]

        tree_entry, created = PageTree.objects.get_or_create(request,
            site = site,
            slug = old_page.shortcut,
            parent = parent,
            defaults = {
                "position": old_page.position,

                "description": old_page.description,

                "type": PageTree.PAGE_TYPE, # FIXME: Find plugin entry in page content

                "design": design,

                "createtime": old_page.createtime,
                "lastupdatetime": old_page.lastupdatetime,
                "createby": old_page.createby,
                "lastupdateby": old_page.lastupdateby,
            }
        )
        if created:
            tree_entry.save(request)
            out.write("PageTree entry '%s' created." % tree_entry.slug)
        else:
            out.write("PageTree entry '%s' exist." % tree_entry.slug)

        page_dict[old_page.id] = tree_entry
        
        #---------------------------------------------------------------------
        # create/get PageMeta entry
        
        pagemeta_entry, created = PageMeta.objects.get_or_create(request,
            page = tree_entry,
            lang = language,
            defaults = {
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
            pagemeta_entry.save(request)
            out.write("PageMeta entry '%s' - '%s' created." % (language, tree_entry.slug))
        else:
            out.write("PageMeta entry '%s' - '%s' exist." % (language, tree_entry.slug))
        
        #---------------------------------------------------------------------
        # create/get PageContent entry

        content_entry, created = PageContent.objects.get_or_create(request,
            page = tree_entry,
            lang = language,
            pagemeta = pagemeta_entry,
            defaults = {
                "content": old_page.content,
                "markup": old_page.markup,

                "createtime": old_page.createtime,
                "lastupdatetime": old_page.lastupdatetime,
                "createby": old_page.createby,
                "lastupdateby": old_page.lastupdateby,
            }
        )
        if created:
            content_entry.save(request)
            out.write("PageContent entry '%s' - '%s' created." % (language, tree_entry.slug))
        else:
            out.write("PageContent entry '%s' - '%s' exist." % (language, tree_entry.slug))

    context = {
        "title": "update data from PyLucid v0.8 to v0.9",
        "results": out.getlines(),
    }
    return render_to_response('pylucid_update/update08result.html', context,
        context_instance=RequestContext(request))


@login_required
def update08(request):
    """ Update PyLucid v0.8 model data to v0.9 models """
    if request.method == 'POST':
        form = UpdateForm(request.POST)
        if form.is_valid():
            site = form.cleaned_data["site"]
            language = form.cleaned_data["language"]

            return _do_update(request, site, language)
    else:
        form = UpdateForm()

    context = {
        "title": "update data from PyLucid v0.8 to v0.9",
        "url": reverse("PyLucidUpdate-update08"),
        "form": form,
    }
    return render_to_response('pylucid_update/update08.html', context,
        context_instance=RequestContext(request))


@login_required
def update08templates(request):
    title = "Update PyLucid v0.8 templates"
    out = SimpleStringIO()
    out.write(title)
    
    def replace(content, out, old, new):
        out.write("replace %r with %r" % (old, new))
        if not old in content:
            out.write("Source string not found, ok.")
        else:
            content = content.replace(old, new)
        return content
        
    
    for template in Template.objects.filter(name__istartswith=settings.SITE_TEMPLATE_PREFIX):       
        out.write("\nUpdate Template: '%s'" % template.name)
        
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
        
        content = replace(content, out,"{% lucidTag page_style %}", new_head_file_tag)
        # temp in developer version:
        content = replace(content, out,"{% lucidTag head_files %}", new_head_file_tag)
        content = replace(content, out,"<!-- ContextMiddleware head_files -->", new_head_file_tag)
        
        content = replace(content, out,"{{ login_link }}", "{% lucidTag auth %}")
        
        content = replace(content, out,"{% lucidTag back_links %}", "<!-- ContextMiddleware breadcrumb -->")
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
        content = replace(content, out,"PAGE.title", "page_title")
        content = replace(content, out,"{{ PAGE.keywords }}", "{{ page_keywords }}")
        content = replace(content, out,"{{ PAGE.description }}", "{{ page_description }}")
        
        content = replace(content, out,"{{ PAGE.datetime", "{{ page_createtime")
        
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
        
        content = replace(content, out,"{{ PAGE.", "{{ page_")
        
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
    

@login_required
def update08styles(request):
    title = "Update PyLucid v0.8 styles"
    out = SimpleStringIO()
    out.write(title)
    
    def replace(content, out, old, new):
        out.write("replace %r with %r" % (old, new))
        if not old in content:
            out.write("String not found. Updated already?")
        else:
            content = content.replace(old, new)
        return content
    
    # Get the file content via django template loader:
    additional_styles, origin = find_template_source("pylucid_update/additional_styles.css")
        
    styles = EditableHtmlHeadFile.objects.filter(filepath__istartswith=settings.SITE_TEMPLATE_PREFIX)
    styles = styles.filter(filepath__iendswith=".css")
    for style in styles:       
        out.write("\nUpdate Styles: '%s'" % style.filepath)
        
        content = style.content
        if additional_styles in content:
            out.write("additional styles allready inserted.")
        else:
            content = additional_styles + content
            style.content = content
            style.save(request)
            out.write("additional styles inserted.")        
    
    context = {
        "title": title,
        "results": out.getlines(),
    }
    return render_to_response('pylucid_update/update08result.html', context,
        context_instance=RequestContext(request))