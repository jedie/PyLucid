# coding: utf-8
"""
    PyLucid App. settings
    ~~~~~~~~~~~~~~~~~~~~~
    
    settings witch only used in the PyLucid app.
"""

# Every Plugin output gets a html DIV or SPAN tag around.
# Here you can defined witch CSS class name the tag should used:
CSS_PLUGIN_CLASS_NAME = "PyLucidPlugins"

EDITABLE_HEAD_LINK_TEMPLATE = "pylucid/headlink_%s_file.html"
HEAD_FILES_URL_PREFIX = "headfile"

# i18n stuff:
FAVORED_LANG_GET_KEY = "lang"
I18N_DEBUG = True # Display many info around detecting current language