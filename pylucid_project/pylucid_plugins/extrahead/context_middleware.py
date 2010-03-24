# coding: utf-8

"""
    PyLucid extrahead context middleware
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    replace <!-- ContextMiddleware extrahead --> in the global page template with
    all extra head html code, stored in request.PYLUCID.extrahead (pylucid.system.extrahead)
    
    Add all headfile links from pagetree.design.headfiles m2m.
    
    PyLucid plugins should use {% extrahead %} block tag (pylucid.defaulttags.extraheadBlock)
    in plugin template for insert e.g. CSS/JS file links into html head.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

__version__= "$Rev:$"

import os
import inspect

from django.conf import settings


class ContextMiddleware(object):
    """ replace <!-- ContextMiddleware extrahead --> in the global page template """
    def __init__(self, request, context):
        self.request = request
        self.extrahead = request.PYLUCID.extrahead # pylucid.system.extrahead
                            
    def _add_pagetree_headfiles(self):
        """ add all headfile links used in the current design. """
        pagetree = self.request.PYLUCID.pagetree
        design = pagetree.design
        
        colorscheme = design.colorscheme
        headfiles = design.headfiles.all()
        
        for headfile in headfiles:
            # Get a instance from pylucid_project.apps.pylucid.system.headfile.HeadfileLink():
            headfilelink = headfile.get_headfilelink(colorscheme)
            head_tag = headfilelink.get_head_tag()
            self.extrahead.append(head_tag)
        
    def render(self):
        """ return all extra head content with all headfiles from current used design """
        self._add_pagetree_headfiles()
        return "\n".join(self.extrahead)

