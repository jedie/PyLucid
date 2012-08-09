# coding: utf-8

"""
    Gallery plugin
    ~~~~~~~~~~~~~~

    :copyleft: 2010-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""


from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_tools.fields.static_path import StaticPathModelField
from django_tools.fields.sign_separated import SignSeparatedModelField
from django_tools.models import UpdateInfoBaseModel

from pylucid_project.apps.pylucid.models import PageTree
from pylucid_project.apps.pylucid.models import Language # import here against import loops


class GalleryModel(UpdateInfoBaseModel):
    """   
    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    pagetree = models.ForeignKey(PageTree, unique=True)

    path = StaticPathModelField(max_length=256,
        help_text=_("Base path after STATIC_ROOT '%s'") % settings.STATIC_ROOT
    )

    template = models.CharField(max_length=256,
        default="gallery/default.html",
        help_text=_("Used template for this gallery")
    )

    filename_whitelist = SignSeparatedModelField(max_length=256,
        default="*.jpg, *.jpeg, *.png",
        help_text=_("fnmatch rules with filename whitelist (comma separated, case insensitive).")
    )
    diritem_blacklist = SignSeparatedModelField(max_length=256,
        default="", null=True, blank=True,
        help_text=_("fnmatch rules for skip directory/files (comma separated, case insensitive).")
    )

    filename_suffix_filter = SignSeparatedModelField(max_length=256,
        default="_WEB, _web",
        help_text=_("suffix to cut from filename (e.g.: my_pic_web.jpg -> my_pic - comma separated).")
    )
    thumb_suffix_marker = SignSeparatedModelField(max_length=256,
        default="_thumb, _tmb",
        help_text=_("suffix in filename to detect the thumbnail picture (comma separated).")
    )

    default_thumb_width = models.PositiveIntegerField(default=100,
        help_text=_("Fallback thumbnail width size, used, if no thumbnail found.")
    )
    default_thumb_height = models.PositiveIntegerField(default=100,
        help_text=_("Fallback thumbnail height size, used, if no thumbnail found.")
    )

    def get_absolute_url(self):
        pagetree_url = self.pagetree.get_absolute_url()
        language_entry = Language.objects.get_current()
        url = "/" + language_entry.code + pagetree_url
        return url

    def __unicode__(self):
        return "GalleryModel for %s" % self.pagetree.get_absolute_url()
