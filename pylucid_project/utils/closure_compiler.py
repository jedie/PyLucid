#!/usr/bin/env python
# coding: utf-8

"""
    static javascript helper
    ~~~~~~~~~~~~~~~~~~~~~~~~
    
    Get JavaScript files and save it compressed.
    use:
        http://code.google.com/closure/compiler/

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import datetime
import json # New in Python v2.6
import os
import pprint
import time
import urllib


class ClosureCompiler(object):
    compile_url = "http://closure-compiler.appspot.com/compile"

    # http://code.google.com/closure/compiler/docs/api-ref.html
    compile_defaults = {
        # Required Request Parameters
        "compilation_level": "SIMPLE_OPTIMIZATIONS",
        "output_format": "json",
        "output_info": ("compiled_code", "statistics"),
    }

    def __init__(self, out_dir):
        self.out_dir = out_dir

    def get_and_save(self, filename, urls):
        print "_" * 79
        print " *** %r ***" % filename
        print "urls:"
        print "\n".join(urls)

        post_data = self.compile_defaults.copy()
        post_data["code_url"] = urls
    #    print post_data
        params = urllib.urlencode(post_data, doseq=True)
    #    print params

        print "request %s..." % self.compile_url,
        start_time = time.time()
        f = urllib.urlopen(self.compile_url, params)
        payload = f.read()
        print "get response in %.2fsec" % (time.time() - start_time)

        response_data = json.loads(payload)
#        pprint.pprint(response_data)
        if not "compiledCode" in response_data:
            print "Response error, response data:"
            pprint.pprint(response_data)
        else:
            code = response_data["compiledCode"]

            statistics = response_data["statistics"]
            print "original size....:", statistics["originalSize"]
            print "compressed size..:", statistics["compressedSize"]
            print "compile time:", statistics["compileTime"]

            out_path = os.path.join(self.out_dir, filename)
            print "Write file %r..." % out_path,
            f = file(out_path, "w")
            f.write("/* content from:\n")
            for url in urls:
                f.write(" * %s\n" % url)
            f.write(" * closure compiled %s */\n" % datetime.date.today().isoformat())
            f.write(code)
            f.close()
            print "OK"

        print "-" * 79
