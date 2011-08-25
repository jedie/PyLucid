#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid install CGI script
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    You should check if the shebang is ok for your environment!
    some examples:
        #!/usr/bin/env python
        #!/usr/bin/env python2.4
        #!/usr/bin/env python2.5
        #!/usr/bin/python
        #!/usr/bin/python2.4
        #!/usr/bin/python2.5
        #!C:\python\python.exe

    :copyleft: 2009-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

print "Content-Type: text/html; charset=utf-8\n"

# turn on traceback manager for CGI scripts
import cgitb; cgitb.enable()

from pprint import pprint
import atexit
import cgi
import codecs
import os
import pwd
import sys
import time
from wsgiref.handlers import CGIHandler


# Save the start time of the current running python instance
start_overall = time.time()


# use utf-8 for all outputs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

# "redirect" stderr output
sys.stderr = sys.stdout


# This must normally not changes, because you should use a local_settings.py file
os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from pylucid_project import VERSION_STRING
print(u"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>%(title)s</title>
<meta http-equiv="expires" content="0" />
<meta name="robots" content="noindex,nofollow" />
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<style type="text/css">/* <![CDATA[ */
html, body {
    padding: 1em 3em 1em 3em;
    background-color: #FFFFEE;
}
body {
    font-family: tahoma, arial, sans-serif;
    color: #000000;
    font-size: 0.9em;
    background-color: #FFFFDB;
    margin: 1em 3em 1em 3em;
    border: 3px solid #C9C573;
}
h1, h2, h3, h4, h5, h6, h7 {
    border-bottom: 1px solid #C9C573;
}
form, pre {
    padding: 1em;
}
pre {
    background-color: #FFFFFF;
    overflow: auto;
}
form, ul, dl {
    background-color: #FFFFEE;
}
/* ]]> */</style>
</head><body>
<h1>%(title)s</h1>
<a name="top"></a>
""" % {"title":u"CGI install - PyLucid v%s" % VERSION_STRING})


def pagestats():
    """ at exit handler """
    # http://code.google.com/p/django-tools/
    from django_tools.template.filters import human_duration
    print "<hr/>"
    print os.environ.get("SERVER_SIGNATURE", "---"),
    print '<p style="text-align:right">render time: %s</p>' % (
        human_duration(time.time() - start_overall)
    )
    print("</body></html>")
atexit.register(pagestats)


from django.conf import settings
from django.core import management
from django.db import connection, backend
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.contrib.sites.models import Site
from django.core.handlers.wsgi import WSGIRequest
from django.middleware.locale import LocaleMiddleware
from django.utils.translation import ugettext as _
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ImproperlyConfigured


ERROR_INFO = "INFO: Have you create a 'local_settings.py' file???"


def call_command(command):
    print "<pre>"
    try:
        management.call_command(command, verbosity=1, interactive=False)
    except ImproperlyConfigured, err:
        etype, evalue, etb = sys.exc_info()
        evalue = etype("Error call %r: %s - %s" % (command, evalue, ERROR_INFO))
        raise etype, evalue, etb
    print "</pre>"
    print "<p><strong>%s done.</strong></p>" % command


def syncdb(request):
    call_command("syncdb")

def migrate(request):
    call_command("migrate")

def loaddata(request):
    print "<pre>"
    management.call_command('loaddata', "pylucid.json", verbosity=1, interactive=False)
    print "</pre>"


def info(request):
    print "<p>Python v%s</p>" % sys.version.replace("\n", " ")
    try:
        username = pwd.getpwuid(os.getuid())[0]
    except Exception, err:
        username = "[Error: %s]" % username
    print "<p>Running under user: <strong>%s</strong></p>" % username
    print "<p>os.uname(): %s</p>" % " - ".join(os.uname())

    print "<ul><h5>sys.path:</h5>"
    for path in sys.path:
        print "<li>%s</li>" % path
    print "</ul>"

    cgi.print_arguments()
    cgi.print_directory()
    cgi.print_environ()
    cgi.print_environ_usage()

def diffsettings(request):
    call_command("diffsettings")

def inspectdb(request):
    call_command("inspectdb")


def database_info(request):
    # http://paste.pocoo.org/show/301/

    print "<pre>"
    print "django db backend name: %s" % backend.Database.__name__
    print "django db backend module: %s\n" % backend.Database.__file__

    try:
        import MySQLdb
    except ImportError, err:
        print "MySQLdb not installed: %s" % err
    else:
        print "MySQLdb v<strong>%s</strong> installed." % ".".join([str(i) for i in MySQLdb.version_info])

    try:
        import sqlite3
    except ImportError, err:
        print "SQlite not installed? - %s" % err
    else:
        print "SQLite v<strong>%s</strong> installed." % ".".join([str(i) for i in sqlite3.sqlite_version_info])

    backend_name = backend.Database.__name__
    if "mysql" in backend_name.lower():
        cursor = connection.cursor()
        print "\nMySQL server encoding:"
        cursor.execute("SHOW VARIABLES LIKE %s;", ("character_set_server",))
        server_encoding = cursor.fetchone()[1]
        print "\tMySQL variable 'character_set_server':", server_encoding
        print

        if server_encoding != "utf8":
            print "Try to change the encoding to utf8"
            sql = "ALTER DATABASE %s CHARACTER SET utf8 COLLATE utf8_unicode_ci;" % settings.DATABASE_NAME
            print sql
            cursor.execute(sql)
            print "OK"

        # http://dev.mysql.com/doc/refman/5.1/en/charset-database.html

        #~ ALTER DATABASE db_name
        #~ [[DEFAULT] CHARACTER SET charset_name]
        #~ [[DEFAULT] COLLATE collation_name]

    print "</pre>"


def setupSites(request):
    """ Check if settings.SITE_ID exist, if not: create it """
    class SiteForm(ModelForm):
        class Meta:
            model = Site

    sid = settings.SITE_ID
    print "<pre>settings.SITE_ID == %r</pre>" % sid

#    Site.objects.all().delete() # Test

    if request.method == 'POST':
        form = SiteForm(request.POST)
        if form.is_valid():
            print "<p>Save new site entry with ID=%s.</p>" % sid
            new_site = form.save(commit=False)
            new_site.id = sid
            new_site.save()

    print "%s existing sites:" % Site.objects.count()
    print "<ul>"
    for site in Site.objects.all():
        print "<li>ID: %s - name: %s</li>" % (site.id, site.name)
    print "</ul>"

    try:
        current_site = Site.objects.get_current()
    except Site.DoesNotExist, err:
        print "<p>Site with ID: %s does not exist." % sid
        print "<small>(%s)</small></p>" % err

        print "<p>Please create this site entry:</p>"
    else:
        print "<p>Site with ID: %s exist, OK.</p>" % current_site.id
        return

    form = SiteForm(initial={
        "name":os.environ.get("SERVER_NAME", ""),
        "domain":os.environ.get("HTTP_HOST", "")
    })

    print(
        '<form action="?setupSites" method="post">'
        '%(form)s'
        '<input type="submit" name="save"/>'
        '</form>'
    ) % {
        "form": form.as_p(),
    }




def create_superuser(request):
    superuser_exist = User.objects.all().filter(is_superuser=True).count()
    if superuser_exist:
        print "<h2>Error: one superuser exist!</h2>"
        print "<p>You can only create one superuser here.<br/>"
        print "Login with as the exsiting user and create new users in"
        print "the django admin panel.</p>"
        return

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            print "<h1>User '%s' created.</h1>" % user.username
            return
    else:
        form = UserCreationForm()

    html = (
        u'<form action="?create_superuser" method="post">'
        '%(form)s'
        '<small><p>Info: Password would be send as plaintext :(</p></small>'
        '<input type="submit" name="save"/>'
        '</form>'
    ) % {
        "form": form.as_p(),
    }
    print html


def print_menu(actions):
    print u"<h2>menu</h2>"
    print u"<ul>"
    for data in actions:
        print u'<li><a href="?%(slug)s"><strong>%(slug)s</strong> - %(title)s</a></li>' % {
            "slug": data["slug"], "title": data["title"]
        }
    print u"</ul>"


actions = [
    {
        "slug": "syncdb",
        "func": syncdb,
        "title": "Creates the database tables for all apps in INSTALLED_APPS",
    },
    {
        "slug": "migrate",
        "func": migrate,
        "title": "Start south migrate",
    },
    {
        "slug": "create_superuser",
        "func": create_superuser,
        "title": "Create a superuser",
    },
    {
        "slug": "loaddata",
        "func": loaddata,
        "title": "insert the initial data",
    },
    {
        "slug": "setupSites",
        "func": setupSites,
        "title": "setup django sites framework",
    },
    {
        "slug": "info",
        "func": info,
        "title": "Display some system informations",
    },
    {
        "slug": "diffsettings",
        "func": diffsettings,
        "title": "Displays differences between the current settings file and Django's default settings.",
    },
    {
        "slug": "inspectdb",
        "func": inspectdb,
        "title": "Introspects the database tables",
    },
    {
        "slug": "database_info",
        "func": database_info,
        "title": "Information about Database backends",
    },
]


def _get_request():
    cgi_handler = CGIHandler()
    cgi_handler.setup_environ()

    request = WSGIRequest(cgi_handler.environ)
    LocaleMiddleware().process_request(request) # init gettext translation
    return request


def main():
    request = _get_request()

    print_menu(actions)

    action_dict = dict([(data["slug"], data) for data in actions])

    query_string = os.environ["QUERY_STRING"]
    if query_string in action_dict:
        print "<hr/><h2>%s</h2>" % query_string
        data = action_dict[query_string]
        print "<h4>%s</h4>" % data["title"]
        func = data["func"]
        func(request)



    #~ print "-"*79


if __name__ == "__main__":
    main()


