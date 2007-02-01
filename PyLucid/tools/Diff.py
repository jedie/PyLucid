#!/usr/bin/python
# -*- coding: UTF-8 -*-

""" kombiniert difflib.Differ() mit Pygments

Used request.render.highlight or request.render.get_hightlighted


 example-1:
----------
    from PyLucid.tools.Diff import display_diff
    display_diff(file_content, db_content, self.request)

 example-2:
----------
    from PyLucid.tools.Diff import get_diff
    html_diff_page = get_diff(file_content, db_content, self.request)
    self.response.write(html_diff_page)


Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""


from difflib import Differ


def display_diff(content1, content2, request):
    """
    write the Diff hightlighted with Pygments directly into the response Object
    """
    diff = make_diff(content1, content2)

    # Mit Pygments anzeigen
    request.render.highlight("diff", diff)

def get_diff(content1, content2):
    """
    returns the HTML-Diff hightlighted with Pygments
    """
    diff = make_diff(content1, content2)

    # Mit Pygments hightlighten
    diff = request.render.get_hightlighted("diff", diff)

    return diff


def make_diff(content1, content2):
    """
    returns the diff as a String, made with difflib.Differ.
    """
    def prepare(content):
        if isinstance(content, (list, tuple)):
            return content

        return content.splitlines()

    content1 = prepare(content1)
    content2 = prepare(content2)

    diff = Differ().compare(content1, content2)

    diff = "\n".join(diff)

    return diff