# coding: utf-8

"""
    PyLucid 'table of contents' plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

__version__ = "$Rev:$"


from django.conf import settings
from django.utils.translation import ugettext as _


def lucidTag(request, min=3):
    """
    Table of contents
    Build a list of all headlines.
    
    Can be inserted into PageContent or into global template.
    
    TOC is displayed only if there exists at least the
    specified number of headings. (lucidTag parameter 'min')
    
    example:
        {% lucidTag TOC %}
        {% lucidTag TOC min=4 %}
    """
    try:
        min = int(min)
    except Exception, err:
        if settings.DEBUG or request.user.is_staff:
            request.page_msg.error(
                _("'min' parameter in lucidTag TOC must be a integer! Error: %s") % err
            )
        min = 3

    # Just save the toc_min_count and return the placeholder
    # The real work would be done in:
    # pylucid_project.middlewares.headline_anchor.HeadlineAnchorMiddleware
    request.PYLUCID._toc_min_count = min
    return settings.PYLUCID.TOC_PLACEHOLDER

