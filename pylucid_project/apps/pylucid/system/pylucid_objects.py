# coding:utf-8

"""
    PyLucid objects
    ~~~~~~~~~~~~~~~
    
    Some need full objects attached to the current request object in pylucid.views.
    
    see also: http://www.pylucid.org/_goto/187/PyLucid-objects/

    :copyleft: 2009-2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import sys

from django.conf import settings
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.utils.log import getLogger

from django_tools.utils.messages import failsafe_message

from pylucid_project.apps.pylucid.preference_forms import SystemPreferencesForm
from pylucid_project.apps.pylucid.system import extrahead
from pylucid_project.utils.escape import escape


# see: http://www.pylucid.org/permalink/443/how-to-display-debug-information
log = getLogger("pylucid-objects")

# max value length in debug __setattr__
MAX_VALUE_LENGTH = 150


class PathInfo(object):
    def __init__(self, request):
        self.raw_path = request.path

    def set_url_lang_info(self, url_lang_code, url_slugs):
        """
        set information fom the requested url.
        e.g.:
            /en/page/sub-page/
        ->
            url_lang_code = "en"
            url_slugs = "page/sub-page"
        """
        log.debug("set_url_lang_info: url_lang_code = %s | url_slugs = %s" % (url_lang_code, url_slugs))
        self.url_lang_code = url_lang_code
        self.url_slugs = url_slugs

    def set_plugin_url_info(self, prefix_url, rest_url):
        """
        set splitted url splugs for PluginPage.
        e.g.:
            /en/Blog/2013/07/25/django-15-support-in-pylucid/
        ->
            prefix_url = "Blog"
            rest_url = "2013/07/25/django-15-support-in-pylucid"
        """
        log.debug("sset_plugin_url_info: prefix_url = %s | rest_url = %s" % (prefix_url, rest_url))
        self.prefix_url = prefix_url
        self.rest_url = rest_url


class PyLucidRequestObjects(object):
    """ PyLucid request objects """
    _check_setattr = False
    def __init__(self, request):
        self.request = request

        self.path_info = PathInfo(request)

        self.preferences_form = SystemPreferencesForm()
        self.preferences = self.preferences_form.get_preferences()

        # FIXME: import here, against import loop:
        from pylucid_project.apps.pylucid.models import Language

        self.languages = Language.objects.get_languages(request)
        self.default_language = Language.objects.get_or_create_default(request)
        try:
            self.current_language = self.languages[0]
        except IndexError, err:
            messages.info(request,
                (
                    "There exist no language on this site!"
                    " Used default one."
                    " Go into 'django admin/PyLucid/Languages' and"
                    " add at least one language to this site!"
                    " (Original error was: %s)"
                ) % err
            )
            self.languages = [self.default_language]
            self.current_language = self.default_language


        # Storing extra html head code from plugins, used in:
        # pylucid.defaulttags.extraheadBlock - redirect {% extrahead %} block tag content
        # pylucid_plugin.extrahead.context_middleware - insert the data into the global page
        self.extrahead = extrahead.ExtraHead()

        # objects witch will be set later:
        # self.object2comment - Object to comment
        # self.pagetree - The current PageTree model instance
        # self.pagemeta - The current PageMeta model instance
        #
        # if current page == PageTree.PAGE_TYPE: # a normal content page
        #     self.pagecontent - PageContent instance, attached at pylucid.views._render_page()
        # elif  current page == PageTree.PLUGIN_TYPE: # a plugin page
        #     self.pluginpage - PluginPage instance, attached at pylucid.system.pylucid_plugin.call_plugin()
        #
        # self.page_template - The global page template as a string
        # self.context - The global context

        self._check_setattr = settings.DEBUG

#     def __getattr__(self, name):
#         try:
#             return super(PyLucidRequestObjects, self).__getattr__(name)
#         except:  # AttributeError:
#             # insert more information into the traceback and re-raise the original error
#             etype, evalue, etb = sys.exc_info()
#             evalue = etype("%s (Forget to use '@pylucid_objects' decorator?)" % evalue)
#             raise etype, evalue, etb

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
            messages.info(self.request, mark_safe(msg))

        super(PyLucidRequestObjects, self).__setattr__(name, value)


if settings.PYLUCID_OBJECTS_DEBUG:
    assert settings.DEBUG == True, "PyLucidRequestObjects works only if settings.DEBUG is on!"
    PyLucidRequestObjects.__setattr__ = PyLucidRequestObjects._setattr_debug

