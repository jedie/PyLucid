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
I18N_DEBUG = False # Display many info around detecting current language

HTML_GET_VIEW_NAME = "html_get_view"