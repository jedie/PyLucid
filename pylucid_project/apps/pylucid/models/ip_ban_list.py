# coding: utf-8

"""
    PyLucid IP ban model
    ~~~~~~~~~~~~~~~~~~~~
    
    A simple model witch contains IP addresses with a timestamp.
    
    TODO: Move IP-Ban + Log stuff into a separate app
        
    e.g. usage in plugins:
    --------------------------------------------------------------------------
    from pylucid_project.apps.pylucid.models import LogEntry, BanEntry
    
    LogEntry.objects.log_action(app_label="plugin_name", action="ban ip", message="Add to ban because...")
    BanEntry.objects.add(request) # raised Http404!
    --------------------------------------------------------------------------

    :copyleft: 2009-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import datetime

from django.http import Http404
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timesince import timesince

from log import LogEntry
from django.db.utils import IntegrityError


class BanEntryManager(models.Manager):
    def cleanup(self, request, timedelta):
        """
        Clean all old BanEntry.
        Creates a log message after delete a BanEntry.
        This method called from pylucid_project.middlewares.ip_ban.IPBanMiddleware
        """
        now = datetime.datetime.now()
        point_in_time = now - timedelta
        queryset = self.all().filter(createtime__lte=point_in_time)
        for entry in queryset:
            if entry.createtime is None:
                # Work-a-round if createtime is None
                entry.createtime = now
                entry.save()
                LogEntry.objects.log_action(
                    app_label="pylucid", action="ip ban error.",
                    request=request,
                    message="Create time is None: %s" % entry,
                )
                return

            try:
                how_old_txt = timesince(entry.createtime, now=datetime.datetime.now())
            except Exception, err:
                # FIXME: e.g.:
                # TypeError: can't subtract offset-naive and offset-aware datetimes
                LogEntry.objects.log_action(
                    app_label="pylucid", action="release ip ban",
                    request=request, message="FIXME: %s" % err,
                )
            else:
                LogEntry.objects.log_action(
                    app_label="pylucid", action="release ip ban",
                    request=request,
                    message="Entry for %s was %s old" % (entry.ip_address, how_old_txt),
                    data={"ip_address": entry.ip_address, "createtime": entry.createtime},
                )
            entry.delete()

    def add(self, request):
        """
        Add current user ban list
        Note: raised 404 after adding the current client to the ban list!
        """
        remote_addr = request.META["REMOTE_ADDR"]
        try:
            self.model(ip_address=remote_addr).save()
        except IntegrityError, err:
            # If a client does many request shortly and get banned we get e.g.:
            # IntegrityError: (1062, "Duplicate entry '123.123.123.123' for key 'PRIMARY'")
            LogEntry.objects.log_action(
                app_label="pylucid", action="add ip ban",
                message="IntegrityError on add %s to ban list: %s" % (remote_addr, err)
            )
        else:
            LogEntry.objects.log_action(
                app_label="pylucid", action="add ip ban",
                message="Add %s to ban list." % remote_addr
            )
            
        raise Http404("You are now banned.")


class BanEntry(models.Model):
    """
    IP Address in this model would be banned in:
        pylucid_project.middlewares.ip_ban.IPBanMiddleware
    The middleware also remove IP after some times with BanEntry.objects.cleanup()
    """
    objects = BanEntryManager()

    ip_address = models.IPAddressField(_('Remote IP Address'),
        primary_key=True, help_text="This IP address will be banned."
    )
    createtime = models.DateTimeField(help_text="Create time")

    def save(self, *args, **kwargs):
        if self.createtime is None:
            # New entry
            now = datetime.datetime.now()
            self.createtime = now
        return super(BanEntry, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"BanEntry %s %s" % (self.ip_address, self.createtime)

    class Meta:
        app_label = 'pylucid'
        verbose_name = _('IP ban entry')
        verbose_name_plural = _('IP ban entries')
        ordering = ('-createtime',)


