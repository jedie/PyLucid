# coding: utf-8

"""
    Log model
    ~~~~~~~~~

    :copyleft: 2009-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _

# http://code.google.com/p/django-tools/
from django_tools.middlewares import ThreadLocal
from django_tools.models import UpdateInfoBaseModel



META_KEYS = (
    "REMOTE_ADDR", "REMOTE_USER", "REQUEST_METHOD", "QUERY_STRING",
    "HTTP_REFERER", "HTTP_USER_AGENT", "HTTP_ACCEPT_ENCODING", "HTTP_ACCEPT_LANGUAGE"
)



class LogEntry(UpdateInfoBaseModel):
    """
    PyLucid action log entries.

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    site = models.ForeignKey(Site,
        #default=Site.objects.get_current
        default=settings.SITE_ID,
    )
    on_site = CurrentSiteManager()

    # Log information:
    app_label = models.CharField(_('App Label'), max_length=255, db_index=True,
        help_text="The App name witch has created this log entry."
    )
    action = models.CharField(_('Action'), max_length=128, db_index=True,
        help_text="Short action key. (e.g.: 'do search', 'login')"
    )
    message = models.CharField(_('Message'), max_length=255, blank=True, null=True,
        help_text="Short/one line log message. (e.g.: 'user FooBar login')"
    )
    long_message = models.TextField(_('long Message'), blank=True, null=True,
        help_text="Complete log message."
    )
    data = models.TextField(blank=True)

    # Own meta data:
    uri = models.CharField(_('URL'), max_length=255,
        help_text="absolute URI form request.build_absolute_uri()"
    )
    used_language = models.ForeignKey("pylucid_migration.Language", blank=True, null=True)

    # Data from request.META
    remote_addr = models.IPAddressField(_('Remote IP Address'), blank=True, null=True, db_index=True,
        help_text="The IP address of the client. From request.META['REMOTE_ADDR']"
    )
    remote_user = models.CharField(_('Remote User'), max_length=255, blank=True, null=True,
        help_text="The user authenticated by the web server, if any. From request.META['REMOTE_USER']"
    )
    request_method = models.CharField(_('Request Method'), max_length=8, blank=True, null=True,
        help_text="Request method, e.g.: 'GET', 'POST'. From request.META['REQUEST_METHOD']"
    )
    query_string = models.CharField(_('Query String'), max_length=255, blank=True, null=True,
        help_text="The query string, as a single **unparsed** string. From request.META['QUERY_STRING']"
    )
    http_referer = models.CharField(_('Referer'), max_length=255, blank=True, null=True,
        help_text="The referring page, if any. From request.META['HTTP_REFERER']"
    )
    http_user_agent = models.CharField(_('User Agent'), max_length=255, blank=True, null=True,
        help_text="The client's user-agent string. From request.META['HTTP_USER_AGENT']"
    )
    http_accept_encoding = models.CharField(_('Accept Encoding'), max_length=255, blank=True, null=True,
        help_text="from request.META['HTTP_ACCEPT_ENCODING']"
    )
    http_accept_language = models.CharField(_('Accept Language'), max_length=255, blank=True, null=True,
        help_text="from request.META['HTTP_ACCEPT_LANGUAGE']"
    )

    def __unicode__(self):
        return u"LogEntry %s %s %s" % (self.createby, self.createtime, self.action)

    class Meta:
        app_label = u'pylucid_migration'
        db_table = u'pylucid_logentry'
        verbose_name = _('log entry')
        verbose_name_plural = _('log entries')
        ordering = ('-createtime',)


