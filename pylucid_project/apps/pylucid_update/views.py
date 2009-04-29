# coding: utf-8

from django.conf import settings
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from dbtemplates.models import Template

from pylucid_project.utils.SimpleStringIO import SimpleStringIO
from pylucid_project.apps.pylucid.models import PageTree, PageContent, Design, EditableHtmlHeadFile
from pylucid_project.apps.pylucid_update.models import Page08, Template08, Style08
from pylucid_project.apps.pylucid_update.forms import UpdateForm




def menu(request):
    """ Display a menu with all update view links """
    context = {
        "title": "menu",
    }
    return render_to_response('pylucid_update/menu.html', context, context_instance=RequestContext(request))

def _update_template(out, content):
    """ update templates """
    content = content.replace("{% lucidTag page_style %}", "{% lucidTag head_files %}")
    out.write("Template updated")
    return content

def _do_update(request, site, language):
    out = SimpleStringIO()
    out.write("Starting update")

    #---------------------------------------------------------------------
    out.write("Move template model")
    templates = {}
    for template in Template08.objects.all():
        new_template_name = settings.SITE_TEMPLATE_PREFIX + template.name + ".html"
        new_content = _update_template(out, template.content)
        new_template, created = Template.objects.get_or_create(
            name = new_template_name,
            defaults = {
                "content": new_content,
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
        new_staticfile, created = EditableHtmlHeadFile.objects.get_or_create(
            filename = style.name + ".css",
            defaults = {
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


    #---------------------------------------------------------------------
    # migrate old page model data

    old_pages = Page08.objects.order_by('parent', 'id').all()

    designs = {}
    page_dict = {}
    for old_page in old_pages:
        #out.write("%s - %s - %s" % (old_page.parent, old_page.id, old_page))

        #---------------------------------------------------------------------
        # create/get Design entry
        
        design_key = "%s %s" % (old_page.template.name, old_page.style.name)
        if design_key not in designs:
            # The template/style combination was not created, yet.
            if old_page.template.name == old_page.style.name:
                new_design_name = old_page.template.name
            else:
                new_design_name = "%s + %s" % (old_page.template.name, old_page.style.name)
                
            design, created = Design.objects.get_or_create(
                name = new_design_name,
                defaults = {
                    "template": templates[old_page.template.name],
                }
            )
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

        tree_entry, created = PageTree.objects.get_or_create(
            id = old_page.id,
            defaults = {
                "site": site,
                "parent": parent,
                "position": old_page.position,

                "slug": old_page.shortcut,
                "description": old_page.description,

                "type": PageTree.PAGE_TYPE, # FIXME: Find plugin entry in page content

                "design": design,

                "createtime": old_page.createtime,
                "lastupdatetime": old_page.lastupdatetime,
                "createby": old_page.createby,
                "lastupdateby": old_page.lastupdateby,
            }
        )
        tree_entry.save()
        if created:
            out.write("PageTree entry '%s' created." % tree_entry.slug)
        else:
            out.write("PageTree entry '%s' exist." % tree_entry.slug)

        page_dict[old_page.id] = tree_entry
        
        #---------------------------------------------------------------------
        # create/get PageContent entry

        content_entry, created = PageContent.objects.get_or_create(
            page = tree_entry,
            lang = language,
            defaults = {
                "title": old_page.title,
                "content": old_page.content,
                "keywords": old_page.keywords,
                "description": old_page.description,

                "markup": old_page.markup,

                "createtime": old_page.createtime,
                "lastupdatetime": old_page.lastupdatetime,
                "createby": old_page.createby,
                "lastupdateby": old_page.lastupdateby,
            }
        )
        content_entry.save()
        if created:
            out.write("PageContent entry '%s' - '%s' created." % (language, tree_entry.slug))
        else:
            out.write("PageContent entry '%s' - '%s' exist." % (language, tree_entry.slug))

    context = {
        "results": out.getlines(),
    }
    return render_to_response('pylucid_update/update08result.html', context,
        context_instance=RequestContext(request))

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
