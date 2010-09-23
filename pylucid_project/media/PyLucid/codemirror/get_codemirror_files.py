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

from pylucid_project.utils.closure_compiler import ClosureCompiler


CODEMIRROR_BASE_URL = "http://marijn.haverbeke.nl/codemirror/js/"
SOURCE_URLS = (
    # Library
    ("codemirror_min.js", [CODEMIRROR_BASE_URL + "codemirror.js"]),
    # base files
    ("codemirror_base.js", [
        CODEMIRROR_BASE_URL + "util.js",
        CODEMIRROR_BASE_URL + "stringstream.js",
        CODEMIRROR_BASE_URL + "select.js",
        CODEMIRROR_BASE_URL + "undo.js",
        CODEMIRROR_BASE_URL + "editor.js",
        CODEMIRROR_BASE_URL + "tokenize.js",
    ]),
    # Parsers
    ("parsecss.js", [CODEMIRROR_BASE_URL + "parsecss.js"]),
    ("tokenizejavascript.js", [CODEMIRROR_BASE_URL + "tokenizejavascript.js"]),
    ("parsejavascript.js", [CODEMIRROR_BASE_URL + "parsejavascript.js"]),
    ("parsecss.js", [CODEMIRROR_BASE_URL + "parsecss.js"]),
    ("parsehtmlmixed.js", [CODEMIRROR_BASE_URL + "parsehtmlmixed.js"]),

    # Contributed parsers
    ("parsepython.js", ["http://marijn.haverbeke.nl/codemirror/contrib/python/js/parsepython.js"]),
    ("parsedjango.js", ["http://github.com/jezdez/django-dbtemplates/raw/master/dbtemplates/media/dbtemplates/js/parsedjango.js"]),
)


if __name__ == "__main__":
    cc = ClosureCompiler(".")
    for filename, urls in SOURCE_URLS:
        cc.get_and_save(filename, urls)



