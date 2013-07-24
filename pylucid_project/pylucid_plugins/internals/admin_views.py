# coding:utf-8

"""
    internals admin views
    ~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2009-2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from pprint import pformat
import os
import posixpath
import sys

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Permission
from django.contrib.contenttypes import generic
from django.core.cache import cache
from django.db import connection, backend
from django.db import models
from django.db.models import get_apps, get_models
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.debug import get_safe_settings

from django_tools.local_sync_cache.local_sync_cache import LocalSyncCache
from django_tools.cache.site_cache_middleware import LOCAL_CACHE_INFO, \
    CACHE_REQUESTS, CACHE_REQUEST_HITS, CACHE_RESPONSES, CACHE_RESPONSE_HITS

from pylucid_project.apps.pylucid.markup import hightlighter
from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid_admin.admin_menu import AdminMenu
from pylucid_project.pylucid_plugins.auth.models import CNONCE_CACHE
from pylucid_project.utils.url_debug import UrlPatternInfo




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

def hightlighted_pformat(obj):
    return hightlighter.make_html(
        pformat(obj, indent=4, width=120), source_type="py", django_escape=True
    )

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


    # Information about the current used url patterns
    urlpatterns = UrlPatternInfo().get_url_info()

    # Create a dict from RequestContext
    request_context = RequestContext(request)
    keys = set()
    for context_dict in request_context.dicts:
        keys = keys.union(set(context_dict.keys()))
    request_context_info = {}
    for key in keys:
        request_context_info[key] = request_context[key]

    try:
        cnonce_size = sys.getsizeof(CNONCE_CACHE)  # New in version 2.6
    except (AttributeError, TypeError):  # PyPy raised a TypeError
        cnonce_size = None

    context = {
        "title": "Show internals",

        "pid": os.getpid(),
        "cache_information": LocalSyncCache.get_cache_information(),

        "permissions": Permission.objects.all(),

        "urlpatterns": urlpatterns,
        "request_context":hightlighted_pformat(request_context_info),
        "settings": hightlighted_pformat(get_safe_settings()),

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
        "os_environ": os.environ,

        # Information of the cache usage
        # from FetchFromCacheMiddleware (if settings.COUNT_FETCH_FROM_CACHE != True: all values are None):
        "local_cache_requests": LOCAL_CACHE_INFO["requests"],
        "local_cache_request_hits": LOCAL_CACHE_INFO["request hits"],
        "global_cache_requests": cache.get(CACHE_REQUESTS),
        "global_cache_request_hits":  cache.get(CACHE_REQUEST_HITS),

        # from UpdateCacheMiddleware (if settings.COUNT_UPDATE_CACHE != True: all values are None):
        "local_cache_responses": LOCAL_CACHE_INFO["responses"],
        "local_cache_response_hits": LOCAL_CACHE_INFO["response hits"],
        "global_cache_responses": cache.get(CACHE_RESPONSES),
        "global_cache_response_hits":  cache.get(CACHE_RESPONSE_HITS),

        # Information about auth cnonce usage:
        "cnonce_count": len(CNONCE_CACHE),
        "cnonce_size": cnonce_size,
        "used_cnonces": tuple(sorted(CNONCE_CACHE.keys())),
    }
    return context


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
                messages.info(request, dir(formfield))
            for a in ('queryset', 'max_length', 'min_length', 'label', 'initial', 'help_text', 'required'):
                if hasattr(formfield, a):
                    attr = getattr(formfield, a)

                    if a in defaults and attr == defaults[a]:
                        # Don't add default key/value combinations into form
                        continue

                    if a in ("label", "help_text"):  # "translate" lazy text
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
        sourcecode = _textform_for_model(model, request)  # , debug=True)

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
        messages.error(request, msg)
        return {"error": msg}

    A = P.AGraph()  # init empty graph

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

    A.layout(prog='dot')  # layout with default (neato)

    filename = "models_graph.png"
    f = file(os.path.join(settings.STATIC_ROOT, filename), "wb")
    f.write(A.draw(format='png'))  # draw png
    f.close()

    context = {
        "url": posixpath.join(settings.STATIC_URL, filename),
    }
    return context

