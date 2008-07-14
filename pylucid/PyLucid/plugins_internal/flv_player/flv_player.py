# -*- coding: utf-8 -*-

"""
    PyLucid flv player plugin
    ~~~~~~~~~~~~~~

    Used http://www.flv-player.net

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__= "$Rev$"

import os, posixpath, fnmatch, pprint

from django.db import models
from django.conf import settings
from django import newforms as forms
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _

from PyLucid.tools.path_manager import media_path_helper
from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.tools.newforms_utils import ChoiceField2
from PyLucid.models import Page, Plugin, Preference

from flv_metadata import FLVReader

#______________________________________________________________________________

def cleanup_flv_metadata(metadata):
    for key in ("width", "height"):
        metadata[key] = int(metadata[key])
    return metadata


class FlashFile(models.Model):
    """
    Contains all flash files with some meta informations.
    """
    fs_path = models.CharField(
        help_text=_(
            "Filesystem path of the file"
            " (Relative to settings.MEDIA_ROOT, include filename)"
        ),
        max_length=255,
        unique = True,
    )

    width = models.PositiveIntegerField(
        help_text=_("width, in pixel, of the flash video"),
    )
    height = models.PositiveIntegerField(
        help_text=_("height, in pixel, of the flash video"),
    )
    raw_metadata = models.TextField(
        help_text=_("The complete FLVReader result dict (in pformat)"),
    )

    preference = models.ForeignKey(
        Preference, related_name="flashfile_preference",
        help_text=_("The used preferences entry for this flash file."),
    )

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)
    createby = models.ForeignKey(
        User, related_name="flashfile_createby",
    )
    lastupdateby = models.ForeignKey(
        User, related_name="flashfile_lastupdateby",
    )

    def get_absolute_url(self):
        """
        Get the absolute url (without the domain/host part)
        """
        return media_path_helper.join_media_url(self.fs_path)

    def get_rel_fs_path(self):
        """
        returns the absolute filesystem path
        """
        return media_path_helper.join_media_path(self.fs_path)

    def get_absolute_fs_path(self):
        """
        returns the absolute filesystem path
        """
        return media_path_helper.abs_media_path(self.fs_path)

    def __unicode__(self):
        return self.fs_path

    class Admin:
        pass
    class Meta:
        app_label = 'PyLucidPlugins'

PLUGIN_MODELS = (FlashFile,)


#
#class PreferencesChoiceField(forms.ModelChoiceField):
#    def label_from_instance(self, obj):
#        return obj.comment
#
#
#class UploadForm(forms.Form):
#    directory = ChoiceField2(
##        choices = MEDIA_DIRS,
#        help_text="Directory for storing the new file. (setting.FILEMANAGER_BASEPATHS)"
#    )
#    preference = PreferencesChoiceField(
#        queryset = Preference.objects.filter(plugin=Plugin.objects.get(plugin_name="flv_player")),
#        #initial = Plugin.objects.get(plugin_name="flv_player").default_pref,
#        help_text="Directory for storing the new file. (setting.FILEMANAGER_BASEPATHS)"
#    )
#    ufile = forms.FileField(
#        label="filename",
#        help_text="Upload a new flash video file"
#    )




class flv_player(PyLucidBasePlugin):

    def _build_flash_vars(self, flv_file, raw_config):
        """
        Build the needed FlashVars value.

        """
        config = raw_config.replace("&amp;", "\n")
        config = raw_config.replace("&", "\n")
        #self.page_msg(config)
        flash_vars = config.splitlines()
        flash_vars.insert(0, "flv=%s" % flv_file)
        self.page_msg(flash_vars)

        values = "&amp;".join(flash_vars)
        values = mark_safe(values)

        return values


    def _render(self, flash_file):
        """
        """
        preference = flash_file.preference
        pref_dict = preference.get_data()

        internal_page_name = pref_dict["internal_page_name"]

        swf_file = pref_dict["swf_file"]
        swf_player = self.internal_page.get_url(swf_file, "swf")
        if swf_player == None:
            self.page_msg.red(
                "Error: Can't find swf player file '%s.swf'." % swf_file
            )

        flv_file = flash_file.get_absolute_url()

        config = pref_dict["config"]
        flash_vars = self._build_flash_vars(flv_file, config)

        context = {
            "flash_vars": flash_vars,
            "width": flash_file.width,
            "height": flash_file.height,
            "swf_player": swf_player,
            "config": config,
        }
        self._render_template(internal_page_name, context, debug=2)

    def lucidTag(self, flv="flash filename"):
        """
        insert the flv player into the cms page
        add a "admin" link, if the user is a admin
        """
        if flv == "flash filename":
            self.page_msg.red("No flash file given")
            return

        try:
            flash_file = FlashFile.objects.get(fs_path = flv)
        except FlashFile.DoesNotExist, err:
            #self.page_msg.red()
            return "[Error: %s]" % err

        return self._render(flash_file)

    def admin_menu(self):
        """
        Build the admin menu use PyLucidBasePlugin.build_menu()
        """
        self.build_menu()

    def _add_flashfile(self, fs_path, pref_obj):

        rel_fs_path = media_path_helper.clean_media_path(fs_path)

        try:
            flash_file = FlashFile.objects.get(fs_path = rel_fs_path)
        except FlashFile.DoesNotExist, err:
            flash_file = FlashFile(
                fs_path = rel_fs_path,
                preference = pref_obj,
                createby = self.request.user,
                lastupdateby = self.request.user,
            )
        else:
            self.page_msg("Update existing entry in FlashFile model.")

        try:
            metadata = FLVReader(fs_path)
        except Exception, err:
            self.page_msg.red("Can't get meta data: %s" % err)
            return

        #self.page_msg("FLV metadata 1:", metadata)
        metadata = cleanup_flv_metadata(metadata)
        #self.page_msg("FLV metadata 2:", metadata)

        flash_file.width = metadata["width"]
        flash_file.height = metadata["height"]
        flash_file.raw_metadata = pprint.pformat(metadata)

        flash_file.save()

        self.page_msg("Add new entry in FlashFile model.")


#        context = {
#            'width': ,
#            'height': ,
#            # FIXME: Ugly path setup:
#            "flv_file": "/" + posixpath.normpath(posixpath.join(rel_path, filename)),
#            # TODO: Save player filename into preferences:
#            "swf_player": self.internal_page.get_url("flv_player_maxi", "swf"),
#        }
#        self._render_template("flv_player_maxi1", context, debug=True)


    def read_filesystem(self):
        """
        Scan the filesystem (settings.MEDIA_ROOT) for existing flash video
        files and add them into the FlashFile model.
        """
        plugin = Plugin.objects.get(plugin_name = self.plugin_name)
        default_pref = plugin.default_pref

        for rel_path, dirs, files in os.walk(settings.MEDIA_ROOT):
            for filename in files:
                if not fnmatch.fnmatch(filename.lower(), '*.flv'):
                    continue

                self.page_msg(rel_path, filename)

                fs_path = os.path.join(rel_path, filename)

                self._add_flashfile(fs_path, default_pref)


    def _handle_upload(self, rel_path, ufile):
        filename = ufile.name

        fs_path = os.path.join(rel_path, filename)

        self.page_msg("Save file to:")
        self.page_msg(fs_path)

        try:
            f = file(fs_path,'wb') # if it exists, overwrite

            for chunk in ufile.chunks():
                f.write(chunk)

            f.close()
        except Exception, e:
            self.page_msg.red("Can't write file: '%s'" % e)
            return

        statinfo = os.stat(fs_path)
        real_filesize = statinfo.st_size

        if real_filesize == ufile.size:
            self.page_msg.green(
                "File '%s' written successfull. (%s Bytes)" % (
                    filename, real_filesize
                )
            )
        else: # Should never appear
            self.page_msg.red(
                "Error writing file '%s'."
                " Filesize is different:"
                " Should be %s Bytes, but is %s Bytes" % (
                    ufile.file_size, real_filesize
                )
            )
            return

        return self._add_flashfile(fs_path)

    def upload(self):
        """
        upload a new flv file
        """
        if self.request.method == 'POST':
            form = UploadForm(self.request.POST, self.request.FILES)
            #self.page_msg(self.request.POST, self.request.FILES)
            if form.is_valid():
                directory = form.cleaned_data["directory"]
                ufile = form.cleaned_data["ufile"]
                return self._handle_upload(directory, ufile)
        else:
            form = UploadForm()

        context = {
            "form": form,
        }
        self._render_template("upload", context)#, debug=True)

    def list_all(self):
        """
        List all existing flash videos entries.
        """
        items = FlashFile.objects.all()

        context = {
            "items": items,
        }
        self._render_template("list_all", context)#, debug=True)
