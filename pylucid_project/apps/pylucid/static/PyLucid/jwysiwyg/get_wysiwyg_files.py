#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid codemirror helper
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Get needed CodeMirror files and save it compressed.
    use:
        http://code.google.com/closure/compiler/

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import subprocess
from pylucid_project.utils.closure_compiler import ClosureCompiler


BASE_URL = "http://github.com/akzhan/jwysiwyg/raw/master/jwysiwyg/"
SOURCE_URLS = (
    ("jquery.wysiwyg.js", [BASE_URL + "jquery.wysiwyg.js"]),
)

WGET_BASE = ("wget", "--timestamp")
WGET_URLS = (
#    BASE_URL + "jquery.wysiwyg.js",
    BASE_URL + "jquery.wysiwyg.css",
    BASE_URL + "jquery.wysiwyg.gif",
    BASE_URL + "jquery.wysiwyg.modal.css",
)


if __name__ == "__main__":
    cc = ClosureCompiler(".")
    for filename, urls in SOURCE_URLS:
        cc.get_and_save(filename, urls)

    print "update via wget:"
    for url in WGET_URLS:
        cmd = WGET_BASE + (url,)
        print "_" * 79
        print "run:", cmd
        subprocess.Popen(cmd).wait()
        print "-" * 79



