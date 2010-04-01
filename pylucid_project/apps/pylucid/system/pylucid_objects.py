# coding:utf-8

"""
    PyLucid objects
    ~~~~~~~~~~~~~~~
    
    Some need full objects attached to the current request object in pylucid.views.
    
    see also: http://www.pylucid.org/_goto/187/PyLucid-objects/

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2009-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings
from django.utils.safestring import mark_safe

from pylucid_project.utils.escape import escape
from pylucid_project.apps.pylucid.shortcuts import failsafe_message
from pylucid_project.apps.pylucid.system import extrahead


# max value length in debug __setattr__
MAX_VALUE_LENGTH = 150


class PyLucidRequestObjects(object):
    """ PyLucid request objects """
    _check_setattr = False
    def __init__(self, request):
        self.request = request

        # FIXME: import here, against import loop:
        from pylucid_project.apps.pylucid.models import Language

        self.languages = Language.objects.get_languages(request)
        self.current_language = self.languages[0]
        self.default_language = Language.objects.get_or_create_default(request)

        # Storing extra html head code from plugins, used in:
        # pylucid.defaulttags.extraheadBlock - redirect {% extrahead %} block tag content
        # pylucid_plugin.extrahead.context_middleware - insert the data into the global page
        self.extrahead = extrahead.ExtraHead()

        # objects witch will be set later:
        #self.pagetree - The current PageTree model instance
        #self.pagemeta - The current PageMeta model instance
        #
        # if current page == PageTree.PAGE_TYPE: # a normal content page
        #     self.pagecontent - PageContent instance, attached at pylucid.views._render_page()
        # elif  current page == PageTree.PLUGIN_TYPE: # a plugin page
        #     self.pluginpage - PluginPage instance, attached at pylucid.system.pylucid_plugin.call_plugin()
        #
        #self.page_template - The global page template as a string
        #self.context - The global context

        self._check_setattr = settings.DEBUG

    def _setattr_debug(self, name, value):
        """
        debug __setattr__ to see if new attributes would be defined or existing changed.
        
        HowTo: http://www.pylucid.org/permalink/133/pylucid-objects#DEBUG
        """
        if self._check_setattr:
            if hasattr(self, name):
                action = "changed"
            else:
                action = "set"

            value_preview = repr(value)
            if len(value_preview) > MAX_VALUE_LENGTH - 3:
                value_preview = value_preview[:MAX_VALUE_LENGTH] + "..."
            value_preview = escape(value_preview)
            msg = "request.PYLUCID.<strong>%s</strong> %s to: <i>%s</i> (type: %s)" % (
                name, action, value_preview, escape(repr(type(value)))
            )
            self.request.page_msg(mark_safe(msg))

        super(PyLucidRequestObjects, self).__setattr__(name, value)


if settings.PYLUCID_OBJECTS_DEBUG:
    assert settings.DEBUG == True, "PyLucidRequestObjects works only if settings.DEBUG is on!"
    PyLucidRequestObjects.__setattr__ = PyLucidRequestObjects._setattr_debug

