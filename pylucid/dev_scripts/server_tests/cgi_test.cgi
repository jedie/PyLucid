#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
    a low level CGI test
    ~~~~~~~~~~~~~~~~~~~~

    Display some Information for a low level test.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

print "Content-Type: text/html;charset=utf-8\n"
import cgitb; cgitb.enable()
print "<h1>PyLucid low level test</h1>"

import os, sys


#______________________________________________________________________________
main_name = __name__
def mod_python_test():
    print "<h3>simple mod_python test</h3>"

    if main_name != "__main__":
        print "Error: __name__ is '%s'<br />" % __name__
        print "Possible not runing as CGI. Running with mod_python?<br />"

    print "GATEWAY_INTERFACE:",
    try:
        gateway = os.environ["GATEWAY_INTERFACE"]
    except KeyError:
        print "Error: Not in os.environ!"
    else:
        print "<strong>%s</strong>" % gateway,
        if gateway=="CGI/1.1":
            print "OK, running as CGI."
        else:
            print "Not running as CGI!"


#______________________________________________________________________________
def python_info():
    print "<h3>Python version:</h3> v%s" % sys.version
    print "<h3>os.uname():</h3>"
    try:
        print " - ".join(os.uname())
    except Exception, e:
        print "Error:", e
    print "<br />"

    print "<h3>sys.path:</h3>"
    sys_path = sys.path[:]
    sys_path.sort()
    for p in sys_path:
        print "%s<br />" % p


#______________________________________________________________________________
def print_module_info():
    def module_info(module_list):
        print "<ul>"
        for module_name in module_list:
            print "<li><strong>%s</strong>:" % module_name
            try:
                module = __import__(module_name, {}, {}, [module_name])
            except ImportError, e:
                print "Import error: %s" % e
            else:
                print "<strong>ok</strong>"
                version = getattr(module, "__version__", None)
                print "__version__:",
                if version:
                    print "<strong>%s</strong>" % version
                else:
                    print "<i>not available.</i>"
            print "</li>"
        print "</ul>"

    print "<h3>Python module info.</h3>"
    print "<h4>Some server handler modules:</h4>"
    module_info(["flup", "mod_python"])
    print "<h4>Some database modules:</h4>"
    module_info(
        [
            "MySQLdb", "sqlite3", "pysqlite2",
            "psycopg", "psycopg2", "cx_Oracle", "adodbapi"
        ]
    )


#______________________________________________________________________________
def environ_info():
    print "<h3>OS-Enviroment:</h3>"
    print '<dl id="environment">'
    keys = os.environ.keys()
    keys.sort()
    for key in keys:
        value = os.environ[key]
        print "<dt>%s</dt>" % key
        print "<dd>%s</dd>" % value
    print "</dl>"


#______________________________________________________________________________
def django_test():
    print "Try to use Django..."
    os.environ["DJANGO_SETTINGS_MODULE"] = "PyLucid.settings"
    #print "os.getcwd() 1:", os.getcwd()
    os.chdir("../../") # go into PyLucid App root folder
    #print "os.getcwd() 2:", os.getcwd()
    sys.path.insert(0, os.getcwd())
    from PyLucid import settings

    print "- setup the django environ...",
    from django.core import management
    management.setup_environ(settings) # init django
    from django.test.utils import setup_test_environment
    setup_test_environment() # django global pre-test setup
    print "OK"


print "<hr />"
mod_python_test()
print "<hr />"
python_info()
print "<hr />"
print_module_info()
print "<hr />"
environ_info()
print "<hr />"
django_test()
print "<hr />"
