# coding:utf-8

from pylucid.models import Language
from pylucid.preference_forms import SystemPreferencesForm

class PyLucidRequestObjects(object):
    """ PyLucid request objects """
    def __init__(self):
        self.system_preferences = SystemPreferencesForm().get_preferences()
        default_lang_code = self.system_preferences["lang_code"]
        self.default_lang_code = default_lang_code
        self.default_lang_entry = Language.objects.get(code=default_lang_code)
        # objects witch will be set later:
        #self.lang_entry - The current language instance