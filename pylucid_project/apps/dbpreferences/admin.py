# coding: utf-8

"""
    dbpreferences.admin
    ~~~~~~~~~~~~~~~~~~~


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.conf.urls.defaults import patterns, url
from django.template.loader import render_to_string

from dbpreferences.models import Preference
from dbpreferences.tools import forms_utils

#------------------------------------------------------------------------------

class PreferenceAdmin(admin.ModelAdmin):
    def edit_link(self, instance):
        """ For adding a edit link into django admin interface """      
        context = {
            "instance": instance,
        }
        return render_to_string('dbpreferences/model_admin_edit_link.html', context)
    edit_link.allow_tags = True
        
    def edit_form(self, request, pk):
        from django.template import RequestContext
        from django.shortcuts import get_object_or_404, render_to_response
        
        obj = Preference.objects.get(pk=pk)
        form_class = obj.get_form_class()
        
        if request.method == 'POST':
            form = form_class(request.POST)
            if form.is_valid():
                data_dict = form.cleaned_data
                user = request.user
                obj.set_data(data_dict, user)
                obj.save()
                
                msg = "Preferences %s updated." % obj
                self.log_change(request, obj, msg)
                
                if request.POST.has_key("_continue"):
                    msg += ' ' + _("You may edit it again below.")
                    
                    if request.REQUEST.has_key('_popup'):
                        next_url = request.path + "?_popup=1"
                    else:
                        next_url = request.path
                else:
                    next_url = reverse("admin_dbpreferences_preference_changelist")
                
                self.message_user(request, msg)
                return HttpResponseRedirect(next_url)
        else:
            data_dict = obj.get_data()
            form = form_class(data_dict)
        
        forms_utils.setup_help_text(form)
        
        context = {
            "title": _('Change %s') % obj,
            "obj": obj,
            "form_url": reverse("admin_dbpref_edit_form", kwargs={"pk": pk}), 
            "form": form,
        }
        return render_to_response("dbpreferences/edit_form.html", context,
            context_instance=RequestContext(request))
    
    def get_urls(self):
        urls = super(PreferenceAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^(?P<pk>\d+)/edit_form/$', self.admin_site.admin_view(self.edit_form),
            name="admin_dbpref_edit_form")
        )
        return my_urls + urls

    list_display = ("site", "app_label", "form_name", "lastupdatetime", "lastupdateby", "edit_link")
    list_display_links = ("form_name",)
    list_filter = ("site", "app_label",)
    search_fields = ("site", "app_label", "form_name",)

admin.site.register(Preference, PreferenceAdmin)
