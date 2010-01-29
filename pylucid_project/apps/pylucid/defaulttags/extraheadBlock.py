# coding: utf-8

"""
    PyLucid {% extrahead %} block tag
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Simple django template block tag. "Redirect" extra head content
    into request.PYLUCID.extrahead
    This data would be inserted with pylucid_plugin.extrahead.context_middleware
    
    PyLucid plugins should use {% extrahead %} block tag in plugin template for
    insert e.g. CSS/JS file links into html head.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django import template

def do_extrahead(parser, token):
    nodelist = parser.parse(('endextrahead',))
    parser.delete_first_token()
    return ExtraheadNode(nodelist)

class ExtraheadNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        """ put head data into pylucid_plugin.head_files.context_middleware """
        output = self.nodelist.render(context)
        try:
            request = context["request"]
        except KeyError:
            raise RuntimeError("Plugin must use RequestContext() or request.PYLUCID.context !")

        extrahead = request.PYLUCID.extrahead
        # FIXME: We check double extrahead entries, but only the whole block. This doesn't work good.
        #        We should check the real link path of every JS/CSS file here.
        # See also: http://trac.pylucid.net/ticket/338
        if output not in extrahead:
            extrahead.append(output)
#            request.page_msg("Insert extrahead:", output)
#        else:
#            request.page_msg("Skip extrahead:", output)
        return u""
