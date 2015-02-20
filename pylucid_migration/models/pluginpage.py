# coding: utf-8

"""
    PyLucid models
    ~~~~~~~~~~~~~~

    :copyleft: 2009-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.db import models

# http://code.google.com/p/django-tools/
from django_tools.models import UpdateInfoBaseModel

from pylucid_migration.base_models.base_models import BaseModel


class PluginPage(BaseModel, UpdateInfoBaseModel):
    """
    A plugin page

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    pagetree = models.OneToOneField("pylucid_migration.PageTree")

    app_label = models.CharField(max_length=768,
        help_text=(
            "The plugin app label witch is in settings.INSTALLED_APPS"
            " (Only apps witch can handle a root url.)"
        )
    )
    urls_filename = models.CharField(max_length=256, default="urls.py",
        help_text="Filename of the urls.py"
    )

    def get_site(self):
        return self.pagetree.site

    def get_absolute_url(self):
        """ absolute url *with* language code (without domain/host part) """
        from pylucid_migration.models.language import Language # import here against import loops

        pagetree_url = self.pagetree.get_absolute_url()
        language_entry = Language.objects.get_current()
        url = "/" + language_entry.code + pagetree_url
        return url

    def get_title(self):
        """ The page title is optional, if not exist, used the slug from the page tree """
        pagemeta = self.get_pagemeta()
        return pagemeta.get_title()

    def get_plugin_name(self):
        return self.app_label.split(".")[-1]

    def get_plugin(self):
        """ returns pylucid_project.system.pylucid_plugins instance """
        plugin_name = self.get_plugin_name()
        plugin_instance = PYLUCID_PLUGINS[plugin_name]
        return plugin_instance

    def __unicode__(self):
        return u"PluginPage '%s' (pagetree: %r)" % (self.app_label, self.pagetree)

    class Meta:
        app_label = u'pylucid_migration'
        db_table = u'pylucid_pluginpage'
        verbose_name_plural = verbose_name = "PluginPage"
        ordering = ("-lastupdatetime",)
#        ordering = ("pagetree", "language")


