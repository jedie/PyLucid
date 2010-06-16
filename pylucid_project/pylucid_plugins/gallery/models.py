# coding:utf-8

from django import http
from django.db import models
from django.utils.translation import ugettext_lazy as _

from pylucid_project.apps.pylucid.models.base_models import UpdateInfoBaseModel
from pylucid_project.apps.pylucid.models import PageTree


class GalleryModel(UpdateInfoBaseModel):
    """   
    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    pagetree = models.ForeignKey(PageTree)

    path = models.CharField(max_length=256,
        help_text=_("Base path after MEDIA_ROOT")
    )

    template = models.CharField(max_length=256,
        default="gallery/default.html",
        help_text=_("Used template for this gallery")
    )

    filename_whitelist = models.CharField(max_length=256,
        default="*.jpg, *.jpeg, *.png",
        help_text=_("fnmatch rules with filename whitelist (comma separated).")
    )
    diritem_blacklist = models.CharField(max_length=256,
        default="", null=True, blank=True,
        help_text=_("fnmatch rules for skip directory/files (comma separated).")
    )

    filename_suffix_filter = models.CharField(max_length=256,
        default="_WEB, _web",
        help_text=_("suffix to cut from filename (e.g.: my_pic_web.jpg -> my_pic - comma separated).")
    )
    thumb_suffix_marker = models.CharField(max_length=256,
        default="_thumb, _tmb",
        help_text=_("suffix in filename to detect the thumbnail picture (comma separated).")
    )

    default_thumb_width = models.PositiveIntegerField(default=100,
        help_text=_("Fallback thumbnail width size, used, if no thumbnail found.")
    )
    default_thumb_height = models.PositiveIntegerField(default=100,
        help_text=_("Fallback thumbnail height size, used, if no thumbnail found.")
    )

    def _comma_split(self, value):
        if value is None:
            return ()
        result = []
        for item in value.split(","):
            item = item.strip()
            if item:
                result.append(item)
        return tuple(result)

    def get_filename_whitelist(self):
        return self._comma_split(self.filename_whitelist)

    def get_diritem_blacklist(self):
        return self._comma_split(self.diritem_blacklist)

    def get_filename_suffix_filter(self):
        return self._comma_split(self.filename_suffix_filter)

    def get_thumb_suffix_marker(self):
        return self._comma_split(self.thumb_suffix_marker)

    def get_absolute_url(self):
        return self.pagetree.get_absolute_url()
