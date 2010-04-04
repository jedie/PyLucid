# coding:utf-8

import os
import sys
import inspect
import posixpath
from pprint import pformat

from django import http
from django import forms
from django.db import models
from django.conf import settings
from django.core import urlresolvers
from django.db import connection, backend
from django.template import RequestContext
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response
from django.views.debug import get_safe_settings
from django.utils.importlib import import_module
from django.db.models import get_apps, get_models
from django.contrib.auth.models import User, Group, Permission
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from pylucid_project.apps.pylucid.markup import hightlighter
from pylucid_project.apps.pylucid.decorators import check_permissions, render_to

from pylucid_project.apps.pylucid_admin.admin_menu import AdminMenu

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
    admin_menu.add_menu_entry(
        parent=menu_section_entry,
        name="show internals", title="Display some internal information.",
        url_name="Internal-show_internals"
    )
    admin_menu.add_menu_entry(
        parent=menu_section_entry,
        name="model_graph", title="Display a model UML graph.",
        url_name="Internal-model_graph"
    )

    return "\n".join(output)

#-----------------------------------------------------------------------------

@check_permissions(superuser_only=True)
@render_to("internals/show_internals.html")
def show_internals(request):
    apps_info = []
    for app in get_apps():
        model_info = []
        for model in get_models(app):
            model_info.append({
                "name":model._meta.object_name,
            })
        apps_info.append({
            "app_name": app.__name__,
            "app_models": model_info,
        })

    # from http://www.djangosnippets.org/snippets/1434/
    # generate a list of (pattern-name, pattern) tuples
    resolver = urlresolvers.get_resolver(None)
    urlpatterns = sorted([
        (key, value[0][0][0])
        for key, value in resolver.reverse_dict.items()
        if isinstance(key, basestring)
    ])

    cache_object_names = ("_url_cache",)
    cache_status = []
    for model_name, model in inspect.getmembers(models, inspect.isclass):
        for cache_object_name in cache_object_names:
            if hasattr(model, cache_object_name):
                cache_obj = getattr(model, cache_object_name)
                cache_status.append({
                    "key":"%s.%s" % (model_name, cache_object_name),
                    "length": len(cache_obj),
                })

    context = {
        "title": "Show internals",

        "cache_status": cache_status,

        "permissions": Permission.objects.all(),

        "urlpatterns": urlpatterns,
        "settings": hightlighter.make_html(
            pformat(get_safe_settings()), source_type="py", django_escape=True
        ),

        "db_backend_name": backend.Database.__name__,
        "db_backend_module": backend.Database.__file__,
        "db_backend_version": getattr(backend.Database, "version", "?"),

        "apps_info": apps_info,

        "db_table_names": sorted(connection.introspection.table_names()),
        "django_tables": sorted(connection.introspection.django_table_names()),

        "request_meta": hightlighter.make_html(
            pformat(request.META), source_type="py", django_escape=True
        ),

        "request_session": hightlighter.make_html(
            pformat(dict(request.session)), source_type="py", django_escape=True
        ),

        "sys_path": sys.path,
    }
    return context

    return render_to_response('internals/show_internals.html', context,
        context_instance=RequestContext(request)
    )

#-----------------------------------------------------------------------------

def _textform_for_model(model, request, debug=False):
    """
    based on http://www.djangosnippets.org/snippets/458/
    """
    defaults = {"required": True, "initial": None, "min_length": None}

    opts = model._meta
    field_list = []
    for f in opts.fields + opts.many_to_many:
        if not f.editable:
            continue
        formfield = f.formfield()
        if formfield:
            kw = []
            if debug:
                request.page_msg(dir(formfield))
            for a in ('queryset', 'max_length', 'min_length', 'label', 'initial', 'help_text', 'required'):
                if hasattr(formfield, a):
                    attr = getattr(formfield, a)

                    if a in defaults and attr == defaults[a]:
                        # Don't add default key/value combinations into form
                        continue

                    if a in ("label", "help_text"): # "translate" lazy text
                        attr = unicode(attr)

                    if a == 'queryset':
                        kw.append("%s=%s" % (a, "%s.objects.all()" % attr.model.__name__))
                    elif attr in [True, False, None]:
                        kw.append("%s=%s" % (a, attr))
                    elif attr:
                        kw.append("%s=_('%s')" % (a, attr))

            f_text = "    %s = forms.%s(%s)" % (f.name, formfield.__class__.__name__ , ', '.join(kw))
            field_list.append(f_text)
    return "class %sForm(forms.Form):\n" % model.__name__ + '\n'.join(field_list)


@check_permissions(superuser_only=True)
@render_to("internals/form_generator.html")
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
        sourcecode = _textform_for_model(model, request)#, debug=True)

        output = hightlighter.make_html(sourcecode, source_type="py")
    else:
        output = None

    context = {
        "title": "Form generator",
        "models_dict": models_dict,
        "output": output,
    }
    return context




@check_permissions(superuser_only=True)
@render_to("internals/model_graph.html")
def model_graph(request):
    try:
        import pygraphviz as P
    except ImportError, err:
        msg = (
            "Error: PyGraphviz can't import!"
            " (Original Error was: %s "
            "- Please note, you need graphviz-dev or graphviz-devel, too.)"
        ) % err
        request.page_msg.error(msg)
        request.page_msg()
        request.page_msg()
        return {"error": msg}

    A = P.AGraph() # init empty graph

    collapse_relation = ("lastupdateby", "createby")

    apps = models.get_apps()
    for app in apps:
        for appmodel in models.get_models(app):
            model_name = appmodel.__module__
            if "pylucid" in model_name:
                color = "green"
            else:
                color = "grey"

            A.add_node(model_name, color=color, shape='box', fontsize="12")

            def add_relation(field):
                if field.name in collapse_relation:
                    return

                target_app = field.rel.to.__module__
                target = field.rel.to.__name__
                field_type = type(field).__name__
                field_name = field.name
                A.add_edge(model_name, target_app,
                    key=field.name, label="%s(%s)" % (field_type, field.name), color=color,
                    fontsize="10",
                )

            for field in appmodel._meta.fields:
                if isinstance(field, (models.ForeignKey, models.OneToOneField)):
                    add_relation(field)

            if appmodel._meta.many_to_many:
                for field in appmodel._meta.many_to_many:
                    if isinstance(field, (models.ManyToManyField, generic.GenericRelation)):
                        add_relation(field)

    A.layout(prog='dot') # layout with default (neato)

    filename = "models_graph.png"
    f = file(os.path.join(settings.MEDIA_ROOT, filename), "wb")
    f.write(A.draw(format='png')) # draw png
    f.close()

    context = {
        "url": posixpath.join(settings.MEDIA_URL, filename),
    }
    return context

