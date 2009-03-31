# coding: utf-8

from django.conf import settings
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from pylucid_project.apps.pylucid.models import PageTree, PageContent
from pylucid_project.apps.pylucid_update.models import Page08
from pylucid_project.apps.pylucid_update.forms import UpdateForm


def menu(request):
    """ Display a menu with all update view links """
    context = {
        "title": "menu",
    }
    return render_to_response('pylucid_update/menu.html', context, context_instance=RequestContext(request))

def _do_update(request, site, language):
    old_pages = Page08.objects.order_by('parent', 'id').all()

    page_dict = {}
    for old_page in old_pages:
        print old_page.parent, old_page.id, old_page

        if old_page.parent == None:
            parent = None
        else:
            parent = page_dict[old_page.parent.id]

        tree_entry = PageTree(
            site = site,
            parent = parent,
            position = old_page.position,

            slug = old_page.shortcut,
            description = old_page.description,

            type = PageTree.PAGE_TYPE, # FIXME: Find plugin entry in page content

        #    template = models.ForeignKey("Template")
        #    style = models.ForeignKey("Style")

            createtime = old_page.createtime,
            lastupdatetime = old_page.lastupdatetime,
            createby = old_page.createby,
            lastupdateby = old_page.lastupdateby,
        )
        tree_entry.save()

        page_dict[old_page.id] = tree_entry

        content_entry = PageContent(
            page = tree_entry,
            lang = language,

            title = old_page.title,
            content = old_page.content,
            keywords = old_page.keywords,
            description = old_page.description,

        #    template = models.ForeinKey("Template")
        #    style = models.ForeignKey("Style")

            markup = old_page.markup,

            createtime = old_page.createtime,
            lastupdatetime = old_page.lastupdatetime,
            createby = old_page.createby,
            lastupdateby = old_page.lastupdateby,
        )
        content_entry.save()

    raise NotImplementedError("Update done... TODO: Display result page")

def update08(request):
    """ Update PyLucid v0.8 model data to v0.9 models """
    if request.method == 'POST':
        form = UpdateForm(request.POST)
        if form.is_valid():
            site = form.cleaned_data["site"]
            language = form.cleaned_data["language"]

            _do_update(request, site, language)
    else:
        form = UpdateForm()

    context = {
        "title": "update data from PyLucid v0.8 to v0.9",
        "form": form,
    }
    return render_to_response('pylucid_update/update08.html', context, context_instance=RequestContext(request))

