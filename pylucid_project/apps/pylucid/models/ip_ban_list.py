# coding: utf-8

"""
    PyLucid IP ban model
    ~~~~~~~~~~~~~~~~~~~~
    
    A simple model witch contains IP addresses with a timestamp.
        
    e.g. usage in plugins:
    --------------------------------------------------------------------------
    from pylucid_project.apps.pylucid.models import LogEntry, BanEntry
    
    LogEntry.objects.log_action(app_label="plugin_name", action="ban ip", message="Add to ban because...")
    BanEntry.objects.add(request) # raised Http404!
    --------------------------------------------------------------------------

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import datetime

from django.http import Http404
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timesince import timesince

from log import LogEntry


class BanEntryManager(models.Manager):
    def cleanup(self, request, timedelta):
        """
        Clean all old BanEntry.
        Creates a log message after delete a BanEntry.
        This method called from pylucid_project.middlewares.ip_ban.IPBanMiddleware
        """
        point_in_time = datetime.datetime.now() - timedelta
        queryset = self.all().filter(createtime__lte=point_in_time)
        for entry in queryset:
            how_old_txt = timesince(entry.createtime, now=datetime.datetime.now())
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
        self.model(ip_address=remote_addr).save()
        raise Http404("Add IP to ban list.")


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
    createtime = models.DateTimeField(auto_now_add=True, help_text="Create time")

    def __unicode__(self):
        return u"BanEntry %s %s" % (self.ip_address, self.createtime)

    class Meta:
        app_label = 'pylucid'
        verbose_name = _('IP ban entry')
        verbose_name_plural = _('IP ban entries')
        ordering = ('-createtime',)


