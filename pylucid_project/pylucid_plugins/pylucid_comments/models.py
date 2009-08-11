# coding: utf-8

from django.db import models
from django.db.models import signals
from django.contrib.comments.models import Comment
from django.utils.translation import ugettext_lazy as _
from django.contrib.comments.signals import comment_was_posted

from pylucid_plugins import update_journal

from pylucid.models import Language


class PyLucidComment(Comment):
    # CurrentSiteManager seems not to work here!
    # But no problem: The parent object should be have a CurrentSiteManager.
    #on_site = CurrentSiteManager()

    title = models.CharField(max_length=300)
    notify = models.BooleanField(
        help_text="Send me a mail if someone replay on my comment. (Needs a email address ;)"
    )
    lang = models.ForeignKey(Language) # Should be set automaticly

    def get_update_info(self):
        """ update info for update_journal.models.UpdateJournal used by update_journal.save_receiver """
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
        verbose_name_plural = _('PyLucid pylucid_comments')

signals.post_save.connect(receiver=update_journal.save_receiver, sender=PyLucidComment)
