# coding: utf-8

"""
    PyLucid extrahead plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from pylucid_project.apps.pylucid.models import EditableHtmlHeadFile



def lucidTag(self, filepath):
    headfile = EditableHtmlHeadFile.objects.get(filepath=filepath)
    html = headfile.get_inline_html()
    return html
