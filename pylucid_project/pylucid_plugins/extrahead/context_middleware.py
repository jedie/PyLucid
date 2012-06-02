# coding: utf-8


"""
    PyLucid extrahead context middleware
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    replace <!-- ContextMiddleware extrahead --> in the global page template with
    all extra head html code, stored in request.PYLUCID.extrahead (pylucid.system.extrahead)
    
    Add all headfile links from pagetree.design.headfiles m2m.
    
    PyLucid plugins should use {% extrahead %} block tag (pylucid.defaulttags.extraheadBlock)
    in plugin template for insert e.g. CSS/JS file links into html head.

    :copyleft: 2009-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""


from django.template.loader import render_to_string


class ContextMiddleware(object):
    """ replace <!-- ContextMiddleware extrahead --> in the global page template """
    def __init__(self, request):
        self.request = request
        self.extrahead = request.PYLUCID.extrahead # pylucid.system.extrahead

    def _add_pagetree_headfiles(self):
        """ add all headfile links used in the current design. """
        pagetree = self.request.PYLUCID.pagetree
        design = pagetree.design
        self.extrahead.append(design.get_headfile_data())

    def render(self):
        """ return all extra head content with all headfiles from current used design """
        self._add_pagetree_headfiles()

#        for entry in self.extrahead:
#            print "***", entry

        return "\n".join(self.extrahead)

