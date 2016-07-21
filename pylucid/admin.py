# coding: utf-8

"""
    PyLucid
    ~~~~~~~

    :copyleft: 2009-2016 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.core import serializers
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from cms.models import Page

from reversion_compare.helpers import patch_admin
from reversion_compare.admin import CompareVersionAdmin

logger = logging.getLogger(__name__)


# Patch django-cms Page Model to add reversion-compare functionality:
# FIXME:
# Traceback (most recent call last):
#   File "./manage.py", line 13, in <module>
#     execute_from_command_line(sys.argv)
#   File "/home/jens/PyLucid_env/lib/python3.4/site-packages/django/core/management/__init__.py", line 354, in execute_from_command_line
#     utility.execute()
#   File "/home/jens/PyLucid_env/lib/python3.4/site-packages/django/core/management/__init__.py", line 328, in execute
#     django.setup()
#   File "/home/jens/PyLucid_env/lib/python3.4/site-packages/django/__init__.py", line 18, in setup
#     apps.populate(settings.INSTALLED_APPS)
#   File "/home/jens/PyLucid_env/lib/python3.4/site-packages/django/apps/registry.py", line 115, in populate
#     app_config.ready()
#   File "/home/jens/PyLucid_env/lib/python3.4/site-packages/django/contrib/admin/apps.py", line 22, in ready
#     self.module.autodiscover()
#   File "/home/jens/PyLucid_env/lib/python3.4/site-packages/django/contrib/admin/__init__.py", line 24, in autodiscover
#     autodiscover_modules('admin', register_to=site)
#   File "/home/jens/PyLucid_env/lib/python3.4/site-packages/django/utils/module_loading.py", line 74, in autodiscover_modules
#     import_module('%s.%s' % (app_config.name, module_to_search))
#   File "/home/jens/PyLucid_env/lib/python3.4/importlib/__init__.py", line 109, in import_module
#     return _bootstrap._gcd_import(name[level:], package, level)
#   File "<frozen importlib._bootstrap>", line 2254, in _gcd_import
#   File "<frozen importlib._bootstrap>", line 2237, in _find_and_load
#   File "<frozen importlib._bootstrap>", line 2226, in _find_and_load_unlocked
#   File "<frozen importlib._bootstrap>", line 1200, in _load_unlocked
#   File "<frozen importlib._bootstrap>", line 1129, in _exec
#   File "<frozen importlib._bootstrap>", line 1471, in exec_module
#   File "<frozen importlib._bootstrap>", line 321, in _call_with_frames_removed
#   File "/home/jens/PyLucid_env/src/pylucid/pylucid/admin.py", line 27, in <module>
#     patch_admin(Page)
#   File "/home/jens/PyLucid_env/src/django-reversion-compare/reversion_compare/helpers.py", line 198, in patch_admin
#     model = model,
# django.contrib.admin.sites.NotRegistered: The model <class 'cms.models.pagemodel.Page'> has not been registered with the admin site.
try:
    patch_admin(Page)
except NotRegistered:
    pass


def export_as_json(modeladmin, request, queryset):
    """
    from:
    http://docs.djangoproject.com/en/dev/ref/contrib/admin/actions/#actions-that-provide-intermediate-pages
    """
    response = HttpResponse(content_type="text/javascript")
    serializers.serialize("json", queryset, stream=response, indent=4)
    return response

# Make export actions available site-wide
admin.site.add_action(export_as_json, 'export_selected_as_json')


from djangocms_text_ckeditor.models import Text
class TextAdmin(CompareVersionAdmin):
    def placeholder_info(self, obj):
        #Page.objects.filter(placeholders)
        placeholder = obj.placeholder
        plugins = placeholder.get_plugins()
        plugin_ids_str = ",".join([str(plugin.pk) for plugin in plugins])
        return "CMSPlugin: %s" % plugin_ids_str

    placeholder_info.short_description = _("placeholder info")
    # placeholder_info.allow_tags = True

    list_display = ("id", "placeholder", "placeholder_info", "language", "plugin_type", "body")
    list_filter = ("language",)
admin.site.register(Text, TextAdmin)