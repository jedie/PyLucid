# coding: utf-8


"""
    PyLucid context processor
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2009-2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import datetime
try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.3, 2.4 fallback.

from django.conf import settings
from django.contrib import messages
from django.contrib.sites.models import Site
from django.utils.log import getLogger
from django.utils.safestring import mark_safe

from dbtemplates.models import Template

from pylucid_project import VERSION_STRING
from pylucid_project.utils import slug



# see: http://www.pylucid.org/permalink/443/how-to-display-debug-information
log = getLogger("pylucid.context_processor")


class NowUpdateInfo(object):
    """
    For adding page update information into context by pylucid context processor
    Useful in plugins views witch allays generate new content (e.g. search result page) 
    """
    def __init__(self, request):
        self.createby = request.user
        self.lastupdateby = request.user
        self.createtime = self.lastupdatetime = datetime.datetime.now()


def add_plugin_info(view_function):
    """ Add css anchor into context. Used information from lucidTagNode. """
    @wraps(view_function)
    def _inner(request):
        context = view_function(request)

        if getattr(request, "plugin_name", None) != None:
            plugin_name = request.plugin_name
            method_name = request.method_name

            log.debug("Add css anchor info for plugin '%s.%s'" % (plugin_name, method_name))

            if not hasattr(request, "css_id_list"):
                request.css_id_list = []

            css_plugin_id = plugin_name + u"_" + method_name
            existing_slugs = request.css_id_list
            css_plugin_id = slug.makeUniqueSlug(css_plugin_id, existing_slugs)

            request.css_id_list.append(css_plugin_id)

            context["css_plugin_id"] = css_plugin_id
            context["css_plugin_class"] = plugin_name

        return context
    return _inner


@add_plugin_info
def pylucid(request):
    """
    A django TEMPLATE_CONTEXT_PROCESSORS
    http://www.djangoproject.com/documentation/templates_python/#writing-your-own-context-processors
    """
    if hasattr(request.PYLUCID, "context"):
        log.debug("reuse a existing context 'request.PYLUCID.context'")
        context = request.PYLUCID.context
    else:
        log.debug("create a new context 'request.PYLUCID.context'")
        context = {
            "powered_by": mark_safe('<a href="http://www.pylucid.org">PyLucid v%s</a>' % VERSION_STRING),
            # This value would be changed in index._render_cms_page(), if the
            # plugin manager or any plugin set request.anonymous_view = False
            "robots": "index,follow",  # TODO: remove in v0.9, see: ticket:161

            "CSS_PLUGIN_CLASS_NAME": settings.PYLUCID.CSS_PLUGIN_CLASS_NAME,

            "current_site": Site.objects.get_current(),
            "sites": Site.objects.all(),

            "PYLUCID": request.PYLUCID,
        }

        pagetree = getattr(request.PYLUCID, "pagetree", None)
        if not pagetree:
            log.debug("no request.PYLUCID.pagetree available.")
        else:
            log.debug("add info to context from 'request.PYLUCID.pagetree'")
            if "design_switch_pk" in request.session:
                # The user has switch the design with pylucid_plugins.design
                from pylucid_project.apps.pylucid.models import Design  # import here, agains import loops

                design_id = request.session["design_switch_pk"]
                try:
                    pagetree.design = Design.on_site.get(id=design_id)
                except Design.DoesNotExist, err:
                    messages.error(request, "Can't switch to design with ID %i: %s" % (design_id, err))
                    del(request.session["design_switch_pk"])

            base_template_name = pagetree.design.template
            # Used e.g.: in plugin templates: {% extends base_template_name %}
            context["base_template_name"] = base_template_name
            log.debug("base_template_name=%s" % base_template_name)

            # Add the dbtemplates entry.
            # Used in pylucid_admin_menu.html for generating the "edit page template" link
            try:
                context["base_template"] = Template.on_site.get(name=base_template_name)
            except Template.DoesNotExist:
                context["base_template"] = None

        pagemeta = getattr(request.PYLUCID, "pagemeta", None)
        if not pagemeta:
            log.debug("no request.PYLUCID.pagemeta available.")
        else:
            log.debug("add info to context from 'request.PYLUCID.pagemeta'")
            context.update({
                "pagemeta": pagemeta,
                "page_title": pagemeta.get_title(),
                "page_keywords": pagemeta.keywords,
                "page_description": pagemeta.description,
                "page_robots": pagemeta.robots,
                "page_language": pagemeta.language.code,
                "page_permalink": pagemeta.get_permalink(),
                "page_absolute_url": pagemeta.get_absolute_url(),
            })

    # Update page updateinfo (a plugin can change it)
    if not hasattr(request.PYLUCID, "updateinfo_object"):
        log.debug("not request.PYLUCID.updateinfo_object available.")
    else:
        log.debug("add info to context from 'request.PYLUCID.updateinfo_object'")
        for itemname in ("createby", "lastupdateby", "createtime", "lastupdatetime"):
            context["page_%s" % itemname] = getattr(request.PYLUCID.updateinfo_object, itemname, None)


    return context
