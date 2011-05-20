# coding: utf-8


"""
    PyLucid extrahead plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.contrib import messages

from pylucid_project.apps.pylucid.models import EditableHtmlHeadFile


def lucidTag(request, filepath):
    """
    Add a headfile inline into the page.
    example:
        {% lucidTag extrahead filepath="/path/to/the/file" %}
    """
    try:
        headfile = EditableHtmlHeadFile.objects.get(filepath=filepath)
    except EditableHtmlHeadFile.DoesNotExist, e:
        msg = u"Wrong headfile path."
        if request.user.is_staff:
            msg += u" (filepath: %r)" % filepath
            messages.error(request, "Headfile with filepath %r doesn't exist: %s" % (filepath, e))
        return "[%s]" % msg


    if not headfile.render:
        colorscheme = None
    else:
        try:
            pagetree = request.PYLUCID.pagetree
            design = pagetree.design
            colorscheme = design.colorscheme
        except AttributeError, e:
            msg = (
                "The headfile %r should be rendered with a colorscheme,"
                " but i can't get one: %s"
            ) % (headfile, e)
            raise AttributeError(msg)

    html = headfile.get_inline_html(colorscheme)

    return html
