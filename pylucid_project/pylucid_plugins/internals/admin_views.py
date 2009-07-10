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

def textform_for_model(model):
    """
    based on http://www.djangosnippets.org/snippets/458/
    """
    opts = model._meta
    field_list = []
    for f in opts.fields + opts.many_to_many:
        if not f.editable:
            continue
        formfield = f.formfield()
        if formfield:
            kw = []
            for a in  ('queryset', 'maxlength', 'label', 'initial', 'help_text', 'required'):
                if hasattr(formfield, a):
                    attr = getattr(formfield, a)
                    if a in ("label", "help_text"): # "translate" lazy text
                        attr = unicode(attr)

                    if a == 'required': # Add required only if it's False
                        if attr == False:
                            kw.append("%s=%s" % (a, attr))
                    elif attr in [True, False, None]:
                        kw.append("%s=%s" % (a, attr))
                    elif a == 'queryset':
                        kw.append("%s=%s" % (a, "%s.objects.all()" % attr.model.__name__))
                    elif attr:
                        kw.append("%s='%s'" % (a, attr))

            f_text = "    %s = forms.%s(%s)" % (f.name, formfield.__class__.__name__ , ', '.join(kw))
            field_list.append(f_text)
    return "class %sForm(forms.Form):\n" % model.__name__ + '\n'.join(field_list)



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
        sourcecode = textform_for_model(model)

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
