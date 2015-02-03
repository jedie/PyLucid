# coding: utf-8

"""
    PyLucid IP ban model
    ~~~~~~~~~~~~~~~~~~~~
    
    A simple model witch contains IP addresses with a timestamp.

    :copyleft: 2009-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _


class BanEntry(models.Model):
    """
    IP Address in this model would be banned in:
        pylucid_project.middlewares.ip_ban.IPBanMiddleware
    The middleware also remove IP after some times with BanEntry.objects.cleanup()
    """
    ip_address = models.IPAddressField(_('Remote IP Address'),
        primary_key=True, help_text="This IP address will be banned."
    )
    createtime = models.DateTimeField(help_text="Create time")

    def __unicode__(self):
        return u"BanEntry %s %s" % (self.ip_address, self.createtime)

    class Meta:
        app_label = u'pylucid_migration'
        db_table = u'pylucid_banentry'
        verbose_name = _('IP ban entry')
        verbose_name_plural = _('IP ban entries')
        ordering = ('-createtime',)


