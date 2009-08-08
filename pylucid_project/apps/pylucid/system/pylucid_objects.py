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

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings

from pylucid.system import extrahead



class PyLucidRequestObjects(object):
    """ PyLucid request objects """
    def __init__(self, request):
        from pylucid.models import Language # FIXME: import here, against import loop.

        self.default_lang_entry = Language.objects.get_default_lang_entry()
        self.default_lang_code = self.default_lang_entry.code

        # Client prefered language instance, use default, if not exist
        self.lang_entry = Language.objects.get_current_lang_entry(request)

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
