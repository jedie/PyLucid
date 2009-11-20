# coding:utf-8

from django import http
from django.db import models

from pylucid.models.base_models import UpdateInfoBaseModel
from pylucid.models import PageTree


class RedirectModel(UpdateInfoBaseModel):
    """   
    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    TYPE_DICT = {
        u"301": {"title": u"301 - PermanentRedirect", "class": http.HttpResponsePermanentRedirect},
        u"302": {"title": u"302 - Redirect", "class": http.HttpResponseRedirect},
    }
    TYPE_CHOICES = [(key, data["title"]) for key, data in TYPE_DICT.iteritems()]
    #--------------------------------------------------------------------------
    
    pagetree = models.ForeignKey(PageTree)
    
    destination_url = models.CharField(max_length=256, help_text="The destination url for the redirect")
    response_type = models.CharField(max_length=3, choices=TYPE_CHOICES, help_text="Response type")

    def get_response_data(self):
        return self.TYPE_DICT[self.response_type]

    def __unicode__(self):
        return u"%s to %s" % (self.get_response_data()["title"], self.destination_url)
