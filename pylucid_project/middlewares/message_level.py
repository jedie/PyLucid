# coding: utf-8

"""
    PyLucid message level middleware
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Set the django message level dynamically
    
    http://docs.djangoproject.com/en/dev/ref/contrib/messages/#changing-the-minimum-recorded-level-per-request

    :copyleft: 2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.contrib.messages import constants as message_constants
from django.contrib import messages


class MessageLevelMiddleware(object):
    def process_request(self, request):
        """
        set the django message level by user type use system preferences.
        """
        # Get the system preferences
        system_preferences = request.PYLUCID.preferences

        # get the level by user type and system preferences
        if request.user.is_superuser:
            level = system_preferences["message_level_superuser"]
        elif request.user.is_staff:
            level = system_preferences["message_level_staff"]
        elif request.user.is_authenticated():
            level = system_preferences["message_level_normalusers"]
        else:
            level = system_preferences["message_level_anonymous"]

        # Set the current used message level
        messages.set_level(request, level)


