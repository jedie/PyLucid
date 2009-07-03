# coding: utf-8

import os

from django import http
from django.conf import settings
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group

from pylucid.models import PageTree, PageMeta, PageContent, PluginPage, Design
from pylucid.preference_forms import SystemPreferencesForm
from pylucid.system import pylucid_plugin, pylucid_objects

from pylucid_project.utils import pylucid_plugins



def menu(request):
    context = {
        "title": "PyLucid admin menu",
    }
    return render_to_response('pylucid_admin/menu.html', context,
        context_instance=RequestContext(request)
    )

def do(request, plugin_name, view_name):
    plugin = pylucid_plugins.PLUGINS[plugin_name]

    response = plugin.call_plugin_view(
        request, settings.ADMIN.VIEW_FILENAME, view_name, method_kwargs={}
    )
    if not isinstance(response, http.HttpResponse):
        raise RuntimeError(
            "Plugin view %s.%s must return a django.http.HttpResponse object! (it returns: %r)" % (
                plugin_name, view_name, type(response)
            )
        )

    return response



def install_pylucid(request):
    output = []
    output.append("*** PyLucid install:")

    sys_pref_form = SystemPreferencesForm()

    # ------------------------------------------------------------------------
    pylucid_admin_group, created = Group.objects.get_or_create(name=settings.ADMIN.USER_GROUP)
    if created:
        output.append("User group '%s' created." % settings.ADMIN.USER_GROUP)
    else:
        output.append("User group '%s' exist." % settings.ADMIN.USER_GROUP)

    # ------------------------------------------------------------------------
    pylucid_admin_design, created = Design.objects.get_or_create(
        name=settings.ADMIN.DESIGN_NAME, defaults={"template": "pylucid_admin/menu.html"}
    )
    # TODO: Add to all sites?
    #design.site.add(site)
    if created:
        output.append("Design '%s' created." % settings.ADMIN.DESIGN_NAME)
    else:
        output.append("Design '%s' exist." % settings.ADMIN.DESIGN_NAME)

    # Add the Design id into the preferences
    sys_pref_form["pylucid_admin_design"] = pylucid_admin_design.id
#
#    # ------------------------------------------------------------------------    
#    pylucid_admin_pagetree, created = PageTree.objects.get_or_create(
#        slug="PyLucidAdmin", parent=None, site=Site.objects.get_current(),
#        defaults={
#            "design": pylucid_admin_design,
#            "type": PageTree.PAGE_TYPE,
#        }
#    )
#    pylucid_admin_pagetree.permitViewGroup = pylucid_admin_group
#
#    url = pylucid_admin_pagetree.get_absolute_url()
#    if created:
#        #tree_entry.save()
#        output.append("PageTree '%s' created." % url)
#    else:
#        output.append("PageTree '%s' exist." % url)
#
#    # Add the PageTree id into the preferences
#    sys_pref_form["pylucid_admin_pagetree"] = pylucid_admin_pagetree.id
#
#    # ------------------------------------------------------------------------
#    pylucid_admin_pagemeta, created = PageMeta.objects.get_or_create(
#        page=pylucid_admin_pagetree,
#        lang=request.PYLUCID.lang_entry, # FIXME: Create in all existing languages?
#        defaults={"name": "PyLucid Admin", "robots":"noindex,nofollow"}
#    )
#    if created:
#        output.append("PageMeta %r created." % pylucid_admin_pagemeta)
#    else:
#        output.append("PageMeta %r exist." % pylucid_admin_pagemeta)
#
#    # ------------------------------------------------------------------------
#    pylucid_admin_pagecontent, created = PageContent.objects.get_or_create(
#        page=pylucid_admin_pagetree,
#        lang=request.PYLUCID.lang_entry, # FIXME: Create in all existing languages?
#        pagemeta=pylucid_admin_pagemeta,
#        defaults={
#            "content":"PyLucid Admin section. Please seletect a menu item.",
#            "markup": PageContent.MARKUP_CREOLE,
#        }
#    )
#    if created:
#        output.append("PageContent %r created." % pylucid_admin_pagecontent)
#    else:
#        output.append("PageContent %r exist." % pylucid_admin_pagecontent)

    # Save new preferences
    sys_pref_form.save()
    output.append("System preferences saved.")

    context = {
        "title": "PyLucid - install",
        "output": output,
    }
    return render_to_response('pylucid_admin/install.html', context,
        context_instance=RequestContext(request)
    )


def install_plugins(request):
    """ Simple call all plugin install view, if exist. """
    output = []

    output.append("*** Install Plugins:")

    for plugin_name, plugin_instance in pylucid_plugins.PLUGINS.iteritems():
        try:
            response = plugin_instance.call_plugin_view(
                request, settings.ADMIN.VIEW_FILENAME, settings.ADMIN.PLUGIN_INSTALL_VIEW_NAME, method_kwargs={}
            )
        except plugin_instance.GetCallableError, err:
            if settings.DEBUG:
                output.append("Skip plugin %r, because it has no install view (%s)" % (plugin_name, err))
        else:
            output.append("_" * 79)
            output.append(" *** install plugin %r ***" % plugin_name)
            assert isinstance(response, basestring) == True, "Plugin install view must return a basestring!"
            output.append(response)

        output.append("")

    context = {
        "title": "PyLucid - Plugin install",
        "output": output,
    }
    return render_to_response('pylucid_admin/install.html', context,
        context_instance=RequestContext(request)
    )