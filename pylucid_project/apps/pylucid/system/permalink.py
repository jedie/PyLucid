# coding: utf-8

"""
more info: http://www.pylucid.org/permalink/319/about-permalink-for-plugin-developers
"""

import posixpath

from django.conf import settings
from django.contrib import messages


#DEBUG = True
DEBUG = False


def plugin_permalink(request, absolute_url):
    """
    Append a additional url part to the normal page permalink.
    e.g.: Deeplink to a blog entry detail view
    """
    current_url = request.PYLUCID.pagemeta.get_absolute_url()

    pagemeta = request.PYLUCID.pagemeta
    page_permalink = pagemeta.get_permalink()

    if not absolute_url.startswith(current_url):
        # Should normally never happen...
        if DEBUG or settings.DEBUG or request.user.is_staff:
            messages.error(request,
                "entry url %r doesn't start with current url %r!" % (absolute_url, current_url)
            )
        return absolute_url # fallback

    additional_url = absolute_url[len(current_url):]
    permalink = posixpath.join(page_permalink, additional_url)

    if DEBUG:
        messages.debug(request, "absolute_url: %r" % absolute_url)
        messages.debug(request, "current_url: %r" % current_url)
        messages.debug(request, "page_permalink: %r" % page_permalink)
        messages.debug(request, "additional_url: %r" % additional_url)
        messages.debug(request, "new permalink: %r" % permalink)

    return permalink
