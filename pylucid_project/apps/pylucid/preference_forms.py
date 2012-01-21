# coding: utf-8

"""
    PyLucid system preferences
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyleft: 2009-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import warnings

from django import forms
from django.contrib import messages
from django.contrib.messages import constants as message_constants
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.messages.api import MessageFailure

from dbpreferences.forms import DBPreferencesBaseForm

from django_tools.middlewares import ThreadLocal

from pylucid_project.apps.pylucid.models import Design


#if Language.objects.count() == 0:
#    # FIXME: Insert first language
#    Language(code="en", description="english").save()
#    warnings.warn("First language 'en' created.")


class SystemPreferencesForm(DBPreferencesBaseForm):
    """ test preferences form """

    # We can't use ModelChoiceField here, is not supported in DBpreferences, yet.
    # see: http://code.google.com/p/django-dbpreferences/issues/detail?id=4
#    pylucid_admin_design = forms.ChoiceField(
#        # choices= Set in __init__, so the Queryset would not execute at startup
#        initial=None,
#        help_text=_("ID of the PyLucid Admin Design. (Not used yet!)")
#    )

    PERMALINK_USE_NONE = "nothing"
    PERMALINK_USE_SLUG = "slug"
    PERMALINK_USE_NAME = "name"
    PERMALINK_USE_TITLE = "title"
    PERMALINK_USE_CHOICES = (
        (PERMALINK_USE_NONE, _("Append no additional text")),
        (PERMALINK_USE_SLUG, _("Append the PageTree slug (language independent)")),
        (PERMALINK_USE_NAME, _("Append the PageMeta name (language dependent)")),
        (PERMALINK_USE_TITLE, _("Append the PageMeta title (language dependent)")),
    )
    permalink_additions = forms.ChoiceField(
        choices=PERMALINK_USE_CHOICES,
        initial=PERMALINK_USE_TITLE,
        help_text=_("Should we append a additional text to every permalink?")
    )

    # Used in pylucid_project.middlewares.pylucid_objects.py
    LOG404_NOTHING = "nothing"
    LOG404_NOREDIRECT = "no_redirect"
    LOG404_EVERYTHING = "everything"
    LOG404_CHOICES = (
        (LOG404_NOTHING, _("Don't log 'Page not found' errors.")),
        (LOG404_NOREDIRECT, _("Log only 'Page not found' if no redirect for the url exists.")),
        (LOG404_EVERYTHING, _("Log every 'Page not found' error, although if redirect exists.")),
    )
    log404_verbosity = forms.ChoiceField(
        choices=LOG404_CHOICES,
        initial=LOG404_NOREDIRECT,
        help_text=_("Setup logging verbosity if 404 - 'Page not found' appears")
    )

    MESSAGE_LEVEL_CHOICES = (
        (message_constants.DEBUG, "Debug (%s)" % message_constants.DEBUG),
        (message_constants.INFO, "Info (%s)" % message_constants.INFO),
        (message_constants.SUCCESS, "Success (%s)" % message_constants.SUCCESS),
        (message_constants.WARNING, "Warning (%s)" % message_constants.WARNING),
        (message_constants.ERROR, "Error (%s)" % message_constants.ERROR),
    )
    message_level_anonymous = forms.ChoiceField(
        choices=MESSAGE_LEVEL_CHOICES,
        initial=message_constants.INFO,
        help_text=_("Set django message level for anonymous user to set the minimum message that will be displayed.")
    )
    message_level_normalusers = forms.ChoiceField(
        choices=MESSAGE_LEVEL_CHOICES,
        initial=message_constants.INFO,
        help_text=_("Set django message level for normal users to set the minimum message that will be displayed.")
    )
    message_level_staff = forms.ChoiceField(
        choices=MESSAGE_LEVEL_CHOICES,
        initial=message_constants.DEBUG,
        help_text=_("Set django message level for staff users to set the minimum message that will be displayed.")
    )
    message_level_superuser = forms.ChoiceField(
        choices=MESSAGE_LEVEL_CHOICES,
        initial=message_constants.DEBUG,
        help_text=_("Set django message level for superusers to set the minimum message that will be displayed.")
    )

    max_log_entries = forms.IntegerField(
        initial=1000, min_value=1,
        help_text=_("The maximal numbers of log entries. After this the oldest log entries would be automatically deleted to protect against overloading."),
    )

    ban_count = forms.IntegerField(
        help_text=_("Numbers of exceptions from one IP within 'ban_time' Sec. after IP would be banned. (Used 'REMOTE_ADDR')"),
        initial=10, min_value=1, max_value=100
    )
    ban_time = forms.IntegerField(
        help_text=_("Time period for count exceptions log messages from the same IP. (Used 'REMOTE_ADDR')"),
        initial=30, min_value=1, max_value=600
    )

#    def __init__(self, *args, **kwargs):
#        super(SystemPreferencesForm, self).__init__(*args, **kwargs)
#        existing_designs = Design.on_site.all().values_list("id", "name")
#
#        self.fields['pylucid_admin_design'].choices = existing_designs
#        self.base_fields['pylucid_admin_design'].choices = existing_designs
#
#        # Fallback if admin design not set
#        initial = existing_designs[0][0]
#        for id, name in existing_designs:
#            if name == "PyLucid Admin":
#                initial = id
#                break
#
#        self.base_fields['pylucid_admin_design'].initial = initial

    def get_preferences(self):
        """
        Fall back to initial data, if something wrong with system preferences.
        This is important, because nothing would work, if validation error raised.
        """
        try:
            return super(SystemPreferencesForm, self).get_preferences()
        except ValidationError, e:
            self.data = self.save_form_init()

            msg = 'Reset system preferences cause: %s' % e
            request = ThreadLocal.get_current_request()
            try:
                messages.info(request, msg)
            except MessageFailure:
                # If message system is not initialized, e.g.:
                # load the system preferences on module level
                warnings.warn(msg)

            return self.data

        return super(SystemPreferencesForm, self).get_preferences()

    class Meta:
        app_label = 'pylucid'
