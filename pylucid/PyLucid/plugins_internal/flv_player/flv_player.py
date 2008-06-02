# -*- coding: utf-8 -*-

"""
    PyLucid flv player plugin
    ~~~~~~~~~~~~~~

    Used http://www.flv-player.net

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__= "$Rev:$"

import os, posixpath

from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django import newforms as forms

from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.models import Page, Plugin

from flv_metadata import FLVReader

#______________________________________________________________________________

from django.db import models
from django.contrib.auth.models import User


class TestModel(models.Model):
    name = models.CharField(unique=True, max_length=150)
    content = models.TextField()

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)

    createby = models.ForeignKey(User, related_name="test_createby",
        null=True, blank=True
    )
    lastupdateby = models.ForeignKey(User, related_name="test_lastupdateby",
        null=True, blank=True
    )
    class Admin:
        pass
    class Meta:
        app_label = 'PyLucidPlugins'

PLUGIN_MODELS = (TestModel,)

#______________________________________________________________________________
# Build a list and a dict from the basepaths
# The dict key is a string, not a integer. (GET/POST Data always returned
# numbers as strings)

BASE_PATHS = [
    (str(no),unicode(path)) for no,path in enumerate(settings.FILEMANAGER_BASEPATHS)
]
BASE_PATHS_DICT = dict(BASE_PATHS)


class UploadForm(forms.Form):
    directory = forms.ChoiceField(
        choices = BASE_PATHS,
        help_text="Directory for storing the new file. (setting.FILEMANAGER_BASEPATHS)"
    )
    ufile = forms.FileField(
        label="filename",
        help_text="Upload a new flash video file"
    )


class flv_player(PyLucidBasePlugin):

#    def lucidTag(self, **kwargs):
#        """
#        insert the flv player into the cms page
#        add a "admin" link, if the user is a admin
#        """
#        self.page_msg("kwargs:", kwargs)

    def _handle_upload(self, dir, ufile):
        rel_path = BASE_PATHS_DICT[dir]

        filename = ufile.filename
        content = ufile.content

        filename = force_unicode(filename)
        joined_path = os.path.join(rel_path, filename)
        abs_fs_path = os.path.abspath(joined_path)

        self.page_msg("Save file to:")
        self.page_msg(abs_fs_path)

        try:
            f = file(abs_fs_path, "wb")
            f.write(content)
            f.close()
        except Exception, err:
            self.page_msg.red("Error saving file: %s" % err)
            return

        try:
            metadata = FLVReader(abs_fs_path)
        except Exception, err:
            self.page_msg.red("Can't get meta data: %s" % err)
            return

        self.page_msg("FLV metadata:", metadata)

        context = {
            'width': int(metadata["width"]),
            'height': int(metadata["height"]),
            # FIXME: Ugly path setup:
            "flv_file": "/" + posixpath.normpath(posixpath.join(rel_path, filename)),
            # TODO: Save player filename into preferences:
            "swf_player": self.internal_page.get_url("flv_player_maxi", "swf"),
        }
        self._render_template("player", context, debug=True)

    def upload(self):
        """
        upload a new flv file
        """
        t = TestModel.objects.all()
        count = len(t)
        self.page_msg(count, t)

        t = TestModel(name = "one entry %s" % count, content = "great!")
        t.save()


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


