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

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

print "Content-Type: text/html; charset=utf-8\n"
print "<h1>Install PyLucid</h1>"

# Debugging für CGI-Skripte 'einschalten'
import cgitb; cgitb.enable()

import cgi, sys, os
from pprint import pprint

sys.stderr = sys.stdout

print "<pre>virtualenv activate...",
try:
    virtualenv_file = os.environ["VIRTUALENV_FILE"]
except KeyError, err:
    print "\nPyLucid - Low-Level-Error!"
    print
    print "environment variable VIRTUALENV_FILE not set:", err
    print "(VIRTUALENV_FILE is the path to './PyLucid_env/bin/activate_this.py')"
    print
    print "</pre>"
    sys.exit()

execfile(virtualenv_file, dict(__file__=virtualenv_file))
print "OK</pre>"

#os.environ['DJANGO_SETTINGS_MODULE'] = "settings"

from django.conf import settings


def syncdb():
    from django.core import management
    print "<pre>"
    management.call_command('syncdb', verbosity=1, interactive=False)
    print "</pre>"
    print "<p><strong>syncdb done.</strong></p>"
    print "<hr/>"

    print "<ul><h4>list of settings.INSTALLED_APPS:</h4>"
    for app_name in settings.INSTALLED_APPS:
        print "<li>%s</li>" % app_name
    print "</ul>"


def info():
    print "<p>Python %s</p>" % sys.version.replace("\n", " ")
    print "<p>os.uname(): %s</p>" % " - ".join(os.uname())

    print "<ul><h5>sys.path:</h5>"
    for path in sys.path:
        print "<li>%s</li>" % path
    print "</ul>"

    cgi.print_arguments()
    cgi.print_directory()
    cgi.print_environ()
    cgi.print_environ_usage()


def mysqldb_info():
    # http://paste.pocoo.org/show/301/

    import MySQLdb
    print "<pre>"
    print "MySQLdb Version:", MySQLdb.__version__
    print "MySQLdb version_info:", MySQLdb.version_info

    from django.db import connection, backend
    print "django db backend name: %s" % backend.Database.__name__
    print "django db backend module: %s" % backend.Database.__file__

    cursor = connection.cursor()
    print "\nMySQL server encoding:"
    cursor.execute("SHOW VARIABLES LIKE %s;", ("character_set_server",))
    server_encoding = cursor.fetchone()[1]
    print "\tMySQL variable 'character_set_server':", server_encoding

    if server_encoding != "utf8":
        print "Try to changen the encoding to utf8"
        sql = "ALTER DATABASE %s CHARACTER SET utf8 COLLATE utf8_unicode_ci;" % settings.DATABASE_NAME
        print sql
        cursor.execute(sql)
        print "OK"

    # http://dev.mysql.com/doc/refman/5.1/en/charset-database.html

    #~ ALTER DATABASE db_name
    #~ [[DEFAULT] CHARACTER SET charset_name]
    #~ [[DEFAULT] COLLATE collation_name]

    print "</pre>"


def setupSites():
    """ Check if settings.SITE_ID exist, if not: create it """
    from django.forms import ModelForm
    from django.contrib.sites.models import Site

    class SiteForm(ModelForm):
        class Meta:
            model = Site

    sid = settings.SITE_ID
    print "<p>settings.SITE_ID == %r</p>" % sid

    #Site.objects.all().delete()

    fs = cgi.FieldStorage()
    if fs.list:
        # Form send via POST
        site_name = fs.getvalue("name")
        site_domain = fs.getvalue("domain")
        post_data = {"name": site_name, "domain": site_domain}
        form = SiteForm(post_data)
        if form.is_valid():
            print "<p>Save site entry.</p>"
            Site(id=sid, name=site_name, domain=site_domain).save()

    try:
        current_site = Site.objects.get_current()
    except Site.DoesNotExist, err:
        print "<p>Site with ID: %s does not exist.<br />" % sid
        print "<small>(%s)</small></p>" % err
        print "Existing sites entries: %r" % cgi.escape(repr(Site.objects.all()))
        print "<p>Please create this site entry:</p>"
    else:
        print "<p>Site with ID: %s exist: '%s', OK.</p>" % (sid, current_site.name)
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
        "form": form,
    }


def create_superuser():
    from django.contrib.auth.models import User

    username = "admin"
    password = "12345678"
    email = "test@test.org"

    defaults = {'password':password, 'email':email}
    user, created = User.objects.get_or_create(
        username=username, defaults=defaults
    )
    user.email = email
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print "<p>Superuser <strong>%s</strong> with password <strong>%s</strong> created." % (
        username, password
    )



def print_menu(actions):
    print "<h2>menu</h2>"
    print "<ul>"
    for key, data in actions.items():
        print '<li><a href="?%(key)s">%(key)s - %(title)s</a></li>' % {
            "key": key, "title": data["title"]
        }
    print "</ul>"


actions = {
    "syncdb": {
        "func":syncdb,
        "title": "Creates the database tables for all apps in INSTALLED_APPS",
    },
    "info": {
        "func":info,
        "title": "Display some system informations",
    },
    "mysqldb_info": {
        "func":mysqldb_info,
        "title": "MySQLdb informations",
    },
    "setupSites": {
        "func": setupSites,
        "title": "setup django sites framework",
    },
    "create_superuser": {
        "func": create_superuser,
        "title": "Create a superuser",
    },
}

print_menu(actions)

query_string = os.environ["QUERY_STRING"]
if query_string in actions:
    print "<hr/><h2>%s</h2>" % query_string
    data = actions[query_string]
    print "<h4>%s</h4>" % data["title"]
    func = data["func"]
    func()

print "<hr/>"
print os.environ.get("SERVER_SIGNATURE", "---")

#~ print "-"*79



