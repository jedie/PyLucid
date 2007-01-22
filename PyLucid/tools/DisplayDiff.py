#!/usr/bin/python
# -*- coding: UTF-8 -*-

""" kombiniert difflib.Differ() mit Pygments


Beispiel:
---------
    from PyLucid.tools.DisplayDiff import display_diff
    display_diff(file_content, db_content, self.request)


Last commit info:
----------------------------------
$LastChangedDate:$
$Rev:$
$Author: jensdiemer $

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""


from difflib import Differ


def display_diff(content1, content2, request):

    def prepare(content):
        if isinstance(content, (list, tuple)):
            return content

        return content.splitlines()

    content1 = prepare(content1)
    content2 = prepare(content2)

    diff = Differ().compare(content1, content2)

    diff = "\n".join(diff)

    # Mit Pygments anzeigen
    request.render.highlight("diff", diff)