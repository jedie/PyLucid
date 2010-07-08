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

import json # New in Python v2.6
import pprint
import sys
import time
import urllib
import datetime


CLOSURE_COMPILTER_URL = "http://closure-compiler.appspot.com/compile"

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

# http://code.google.com/closure/compiler/docs/api-ref.html
DEFAULTS = {
    # Required Request Parameters
    "compilation_level": "SIMPLE_OPTIMIZATIONS",
    "output_format": "json",
    "output_info": "compiled_code",
}

def get_and_save(filename, urls):
    print "_"*79
    print " *** %r ***" % filename
    print "urls:"
    print "\n".join(urls)
    
    post_data = DEFAULTS.copy()
    post_data["code_url"] = urls
#    print post_data
    params = urllib.urlencode(post_data, doseq=True)
#    print params
    
    print "request %s..." % CLOSURE_COMPILTER_URL,
    start_time = time.time()
    f = urllib.urlopen(CLOSURE_COMPILTER_URL, params)
    payload = f.read()
    print "get response in %.2fsec" % (time.time()-start_time)
    
    response_data = json.loads(payload)
    if not "compiledCode" in response_data:
        print "Response error, response data:"
        pprint.pprint(response_data)
    else:
        code = response_data["compiledCode"]
        print "compressed code length:", len(code)
        print "Write file...",
        f = file(filename, "w")
        f.write("/* content from:\n")
        for url in urls:
            f.write(" * %s\n" % url)
        f.write(" * closure compiled %s */\n" % datetime.date.today().isoformat())
        f.write(code)
        f.close()
        print "OK"
        
    print "-"*79

if __name__ == "__main__":
    for filename, urls in SOURCE_URLS:
        get_and_save(filename, urls)



