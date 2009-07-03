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

from pylucid.models import Language
from pylucid.system import extrahead
from pylucid.preference_forms import SystemPreferencesForm


class PyLucidRequestObjects(object):
    """ PyLucid request objects """
    def __init__(self, request):
        self.system_preferences = SystemPreferencesForm().get_preferences()
        default_lang_code = self.system_preferences["lang_code"]
        self.default_lang_code = default_lang_code
        self.default_lang_entry = Language.objects.get(code=default_lang_code)

        # The current language instance
        try:
            self.lang_entry = Language.objects.get(code=request.LANGUAGE_CODE)
        except Language.DoesNotExist:
            self.lang_entry = self.default_lang_entry
            if settings.PYLUCID.I18N_DEBUG:
                request.page_msg.error(
                    'Favored language "%s" does not exist -> use default lang from system preferences' % (
                        request.LANGUAGE_CODE
                    )
                )

        # Storing extra html head code from plugins, used in:
        # pylucid.defaulttags.extraheadBlock - redirect {% extrahead %} block tag content
        # pylucid_plugin.extrahead.context_middleware - insert the data into the global page
        self.extrahead = extrahead.ExtraHead()

        # objects witch will be set later:
        #self.pagetree - The current PageTree model instance
        #self.pagemeta - The current PageMeta model instance
        #self.pagecontent - PageContent instance, but only if the current page is not a PagePlugin!
        #self.page_template - The globale page template as a string
        #self.context - The globale context
