# coding: utf-8

from django.db import models
from django.contrib import admin
from django.db.models import signals
from django.contrib.comments.models import Comment
from django.utils.translation import ugettext_lazy as _
from django.contrib.comments.signals import comment_was_posted

from pylucid_admin.admin import pylucid_admin_site

from pylucid_plugins import page_update_list

from pylucid.models import PageContent, Language



class PyLucidComment(Comment):
    title = models.CharField(max_length=300)
    lang = models.ForeignKey(Language)

    def get_update_info(self):
        """ update info for page_update_list.models.UpdateJournal used by page_update_list.save_receiver """
        if self.is_public == False or self.is_removed == True: # Don't list non public articles
            return

        return {
            "lastupdatetime": self.submit_date,
            "user_name": self.userinfo["name"],
            "lang": self.lang,
            "object_url": self.get_absolute_url(),
            "title": self.title,
        }

    class Meta:
        verbose_name = _('PyLucid comment')
        verbose_name_plural = _('PyLucid comments')

signals.post_save.connect(receiver=page_update_list.save_receiver, sender=PyLucidComment)



class PyLucidCommentAdmin(admin.ModelAdmin):
    pass
#    list_display = ("id", "headline", "is_public", "get_absolute_url", "lastupdatetime", "lastupdateby")
#    list_display_links = ("headline",)
#    list_filter = ("is_public", "createby", "lastupdateby",)
#    date_hierarchy = 'lastupdatetime'
#    search_fields = ("headline", "content")

pylucid_admin_site.register(PyLucidComment, PyLucidCommentAdmin)
