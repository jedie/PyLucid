
"""
setup some "static" variables
"""

from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

from PyLucid import PYLUCID_VERSION_STRING
from PyLucid.tools.shortcuts import makeUnique

from django.conf import settings

def static(request):
    """
    A django TEMPLATE_CONTEXT_PROCESSORS
    http://www.djangoproject.com/documentation/templates_python/#writing-your-own-context-processors
    """
    context_extras = {}

    #___________________________________________________________________________

    context_extras['powered_by'] = mark_safe(
        '<a href="http://www.pylucid.org">PyLucid v%s</a>' \
                                                        % PYLUCID_VERSION_STRING
    )

    #___________________________________________________________________________

    # The module_manager set "must_login":
    if getattr(request, "must_login", False):
        context_extras["robots"] = "NONE,NOARCHIVE"
    else:
        context_extras["robots"] = "index,follow"

    #___________________________________________________________________________

    return context_extras



def add_dynamic_context(request, context):
    """
    Add some dynamic stuff into the context.
    """
    URLs = context["URLs"]

    #___________________________________________________________________________

    if request.user.username != "":
        # User is logged in
        url = URLs.commandLink("auth", "logout")
        txt = "%s [%s]" % (_("Log out"), request.user.username)
    else:
        url = URLs.commandLink("auth", "login/?next=%s" % request.path)
        txt = _("Log in")

    context["login_link"] = mark_safe(
        '<a href="%s">%s</a>' % (url, txt)
    )
    
    # Put the language information into the context, if it exists.
    # see: http://www.djangoproject.com/documentation/i18n/
    if hasattr(request, 'session') and 'django_language' in request.session:
        context['django_language']=request.session['django_language']
    else:
        context['django_language']=''



def add_css_tag(context, content, plugin_name, method_name):
    """
    Add a unique CSS-ID and a class name defined in the settings.py
    """
    id = plugin_name + u"_" + method_name
    id = makeUnique(id, context["CSS_ID_list"])
    context["CSS_ID_list"].append(id)
    class_name = getattr(settings, "CSS_PLUGIN_CLASS_NAME", "PyLucidPlugins")

    try:
        return u'<div class="%s %s" id="%s">\n%s\n</div>\n' % (
            class_name, plugin_name, id, content
        )
    except UnicodeDecodeError:
        # FIXME: In some case (with mysql_old) we have trouble here.
        # I get this traceback on www.jensdiemer.de like this:
        #
        #Traceback (most recent call last):
        #File ".../django/template/__init__.py" in render_node
        #    750. result = node.render(context)
        #File ".../PyLucid/defaulttags/lucidTag.py" in render
        #    102. content = self._add_unique_div(context, content)
        #File ".../PyLucid/defaulttags/lucidTag.py" in _add_unique_div
        #    73. return u'<div class="%s" id="%s">\n%s\n</div>\n' % (
        #
        #UnicodeDecodeError at /FH-D-sseldorf/
        #'ascii' codec can't decode byte 0xc3 in position 55: ordinal not in range(128)
        #
        #content += "UnicodeDecodeError hack active!"
        return '<span class="%s %s" id="%s">\n%s\n</span>\n' % (
            class_name, str(plugin_name), str(id), content
        )
