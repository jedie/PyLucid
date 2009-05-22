
"""
setup some "static" variables
"""

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from pylucid_project import PYLUCID_VERSION_STRING
from pylucid_project.utils import slug


def _add_plugin_info(request, context):
    """ Add css anchor into context. Used infomation from lucidTagNode. """
    
    plugin_name = request.plugin_name
    method_name = request.method_name
    
    if not hasattr(request, "css_id_list"):
        request.css_id_list = []
    
    css_plugin_id = plugin_name + u"_" + method_name
    existing_slugs = request.css_id_list
    css_plugin_id = slug.makeUniqueSlug(css_plugin_id, existing_slugs)
    
    request.css_id_list.append(css_plugin_id)
    
    context["css_plugin_id"] = css_plugin_id
    context["css_plugin_class"] = plugin_name
    
    return context
    


def pylucid(request):
    """
    A django TEMPLATE_CONTEXT_PROCESSORS
    http://www.djangoproject.com/documentation/templates_python/#writing-your-own-context-processors
    """
    current_site = Site.objects.get_current()
    all_sites = Site.objects.all()
    
    context = {
        "powered_by": mark_safe('<a href="http://www.pylucid.org">PyLucid v%s</a>' % PYLUCID_VERSION_STRING),
        # This value would be changed in index._render_cms_page(), if the
        # plugin manager or any plugin set request.anonymous_view = False
        "robots": "index,follow", # TODO: remove in v0.9, see: ticket:161
        
        "CSS_PLUGIN_CLASS_NAME": settings.PYLUCID.CSS_PLUGIN_CLASS_NAME,
        
        "current_site": current_site,
        "sites": all_sites,
    }
    
    
    
    # TODO: Use internal SHA-Login plugin views, if implemented:
    if request.user.is_authenticated():
        # admin_logout reverse is still broken in django, see:
        # http://code.djangoproject.com/ticket/11080
        # http://code.djangoproject.com/attachment/ticket/10061
        #url = reverse("admin_logout")
        #url = reverse("admin_index") + "logout/" # TODO: Update this if django is bugfixed
        url = "?auth=logout"
        
        txt = "%s [%s]" % (_("Log out"), request.user.username)
    else:
        #url = reverse("admin_index") # django admin panel index page
        url = "?auth=login"
        txt = _("Log in")
        
    context["login_link"] = mark_safe('<a href="%s">%s</a>' % (url, txt))
    
    if hasattr(request, "plugin_name"):
        # Add css anchor info
        context = _add_plugin_info(request, context)
    
    return context

#
#def add_dynamic_context(request, context):
#    """
#    Add some dynamic stuff into the context.
#    """
#
#    # Put the language information into the context, if it exists.
#    # see: http://www.djangoproject.com/documentation/i18n/
#    if hasattr(request, 'session') and 'django_language' in request.session:
#        context['django_language']=request.session['django_language']
#    else:
#        context['django_language']=''
#
#
#def add_css_tag(context, content, plugin_name, method_name):
#    """
#    Add a unique CSS-ID and a class name defined in the settings.py
#    """
#    id = plugin_name + u"_" + method_name
#    id = makeUnique(id, context["CSS_ID_list"])
#    context["CSS_ID_list"].append(id)
#    class_name = getattr(settings, "CSS_PLUGIN_CLASS_NAME", "PyLucidPlugins")
#
#    try:
#        return (
#            u'<div class="%(c)s %(p)s" id="%(id)s">\n'
#            '%(content)s\n'
#            '</div>\n'
#        ) % {
#            "c": class_name, "p": plugin_name, "m": method_name,
#            "id": id, "content": content,
#        }
#    except UnicodeDecodeError:
#        # FIXME: In some case (with mysql_old) we have trouble here.
#        # I get this traceback on www.jensdiemer.de like this:
#        #
#        #Traceback (most recent call last):
#        #File ".../django/template/__init__.py" in render_node
#        #    750. result = node.render(context)
#        #File ".../PyLucid/defaulttags/lucidTag.py" in render
#        #    102. content = self._add_unique_div(context, content)
#        #File ".../PyLucid/defaulttags/lucidTag.py" in _add_unique_div
#        #    73. return u'<div class="%s" id="%s">\n%s\n</div>\n' % (
#        #
#        #UnicodeDecodeError at /FH-D-sseldorf/
#        #'ascii' codec can't decode byte 0xc3 in position 55: ordinal not in range(128)
#        #
#        #content += "UnicodeDecodeError hack active!"
#        return (
#            '<div class="%(c)s %(p)s" id="%(id)s">\n'
#            '%(content)s\n'
#            '</div>\n'
#        ) % {
#            "c": class_name, "p": str(plugin_name), "m": str(method_name),
#            "id": str(id), "content": content,
#        }
