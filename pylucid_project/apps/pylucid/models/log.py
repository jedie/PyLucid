# coding: utf-8

"""
    TODO:
    * handel proxy's 'HTTP_X_FORWARDED_FOR' values.
        See notes here:
        http://docs.djangoproject.com/en/1.0/ref/middleware/#reverse-proxy-middleware
"""

import datetime

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.admin.util import quote
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager

# http://code.google.com/p/django-tools/
from django_tools.middlewares import ThreadLocal

# http://code.google.com/p/django-dbpreferences/
from dbpreferences.fields import DictField

from pylucid.models.base_models import UpdateInfoBaseModel


META_KEYS = (
    "REMOTE_ADDR", "REMOTE_USER", "REQUEST_METHOD", "QUERY_STRING",
    "HTTP_REFERER", "HTTP_USER_AGENT", "HTTP_ACCEPT_ENCODING", "HTTP_ACCEPT_LANGUAGE"
)

class LogEntryManager(models.Manager):
    def get_same_remote_addr(self, request):
        """
        return a QuerySet with all entries from the current remote Address.
        """
        current_remote_addr = request.META["REMOTE_ADDR"]
        queryset = self.model.on_site.all()
        queryset = queryset.filter(remote_addr=current_remote_addr)
        return queryset

    def last_remote_addr_actions(self, request, timedelta):
        """
        creates a queryset with all items from the same REMOTE_ADDR in the timedelta point of time.
        """
        assert isinstance(timedelta, datetime.timedelta)

        queryset = self.get_same_remote_addr(request)

        point_in_time = datetime.datetime.utcnow() - timedelta
        queryset = queryset.filter(createtime__gte=point_in_time)

        return queryset

    def log_action(self, app_label, action, request=None, message=None, data=None):
        if request is None:
            request = ThreadLocal.get_current_request()

        kwargs = {
            "uri": request.build_absolute_uri(),
            "app_label": app_label,
            "action": action,
            "message": message,
            "data": data,
        }

        if hasattr(request, "PYLUCID"):
            kwargs["used_language"] = request.PYLUCID.language_entry

        for key in META_KEYS:
            value = request.META.get(key)
            if value and len(value) > 255:
                value = "%s..." % value[:252]
            kwargs[key.lower()] = value

        e = self.model(**kwargs)
        e.save()


class LogEntry(UpdateInfoBaseModel):
    """
    PyLucid action log entries.

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    objects = LogEntryManager()

    site = models.ForeignKey(Site, default=Site.objects.get_current)
    on_site = CurrentSiteManager()

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

    # Own meta data:
    used_language = models.ForeignKey("Language", blank=True, null=True)
    uri = models.CharField(_('URL'), max_length=255,
        help_text="absolute URI form request.build_absolute_uri()"
    )

    # Log information:
    app_label = models.CharField(_('App Label'), max_length=255, db_index=True,
        help_text="The App name witch has created this log entry."
    )
    action = models.CharField(_('Action'), max_length=128, db_index=True,
        help_text="Short action key. (e.g.: 'do search', 'login')"
    )
    message = models.CharField(_('Message'), max_length=255, blank=True, null=True,
        help_text="Complete log message. (e.g.: 'user FooBar login')"
    )
    # From django-dbpreferences
    data = DictField(blank=True, null=True,
        help_text="serialized preference form data dictionary")

    def __unicode__(self):
        return u"LogEntry %s %s %s" % (self.createby, self.createtime, self.action)

    class Meta:
        app_label = 'pylucid'
        verbose_name = _('log entry')
        verbose_name_plural = _('log entries')
        ordering = ('-createtime',)


