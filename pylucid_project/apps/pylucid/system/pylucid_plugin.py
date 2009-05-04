# coding: utf-8

"""
    PyLucid plugin tools
    ~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.p

"""

__version__= "$Rev:$"

import sys

from django.conf import settings
from django.http import HttpResponse
from django.core import urlresolvers



def call_plugin_view(request, plugin_name, method_name, method_kwargs={}):
    """
    """
    # callback is either a string like 'foo.views.news.stories.story_detail'
    callback = "pylucid_plugins.%s.views.%s" % (plugin_name, method_name)
    try:
        callable = urlresolvers.get_callable(callback)
    except (ImportError, AttributeError), err:
        raise GetCallableError(err)
    
    # Add info for pylucid_project.apps.pylucid.context_processors.pylucid
    request.plugin_name = plugin_name
    request.method_name = method_name
    
    # call the plugin view method
    response = callable(request, **method_kwargs)
    
    return response
    


class GetCallableError(Exception):
    pass