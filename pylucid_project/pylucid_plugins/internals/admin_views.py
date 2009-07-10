# coding:utf-8

from django import forms
from django.db import models
from django.core import urlresolvers
from django.template import RequestContext, mark_safe
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _

from pylucid.markup import hightlighter
from pylucid.models import PageTree, PageMeta, PageContent, PyLucidAdminPage, Design

from pylucid_admin.admin_menu import AdminMenu

def install(request):
    """ insert PyLucid admin views into PageTree """
    output = []

    admin_menu = AdminMenu(request, output)
    menu_section_entry = admin_menu.get_or_create_section("internals")

    admin_menu.add_menu_entry(
        parent=menu_section_entry,
        name="form generator", title="Form generator from existing models.",
        url_name="Internal-form_generator"
    )

    return "\n".join(output)

def _form_generator(model):
    output = []
    fields = model._meta.fields + model._meta.many_to_many

    output.append("class %sForm(forms.Form):" % (model.__class__.__name__))
    for field in fields:
        formfield = field.formfield()
        if formfield:
            fieldtype = str(formfield).split()[0].split('.')[-1]
            print field.name, field
            arguments = {}
            if field.verbose_name != field.name:
                arguments['verbose_name'] = '\'%s\'' % field.verbose_name
            if field.help_text:
                arguments['help_text'] = '\'%s\'' % field.help_text
            if field.blank:
                arguments['required'] = False

            output.append("    %s = forms.%s(%s)" % (
                field.name, fieldtype, ', '.join(['%s=%s' % (k, v) for k, v in arguments.iteritems()])
            ))
    return output

def form_generator(request, model_no=None):
    apps = models.get_apps()
    app_models = []
    for app in apps:
        app_models += models.get_models(app)

    models_dict = {}
    for no, model in enumerate(app_models):
        models_dict[no] = model

    if model_no:
        model = models_dict[int(model_no)]
        lines = _form_generator(model)
        sourcecode = "\n".join(lines)
        output = hightlighter.make_html(sourcecode, source_type="py")
        output = mark_safe(output)
    else:
        output = None

    context = {
        "title": "Form generator",
        "models_dict": models_dict,
        "output": output,
    }

    return render_to_response('internals/form_generator.html', context,
        context_instance=RequestContext(request)
    )
