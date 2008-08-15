#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid CGI dispatcher
    ~~~~~~~~~~~~~~~~~~~~~~

    You should check if the shebang is ok for your environment!
    some examples:
        #!/usr/bin/env python
        #!/usr/bin/env python2.4
        #!/usr/bin/env python2.5
        #!/usr/bin/python
        #!/usr/bin/python2.4
        #!/usr/bin/python2.5
        #!C:\python\python.exe

    If settings.DEBUG is ON:
      - all write to stdout+stderr are checked. It's slow!
      - Its guaranteed that a HTML Header would be send first.

    It used the cgi_server.py shipped with PyLucid.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

#print "Content-type: text/html; charset=utf-8\r\n\r\nHARDCORE DEBUG:\n"
#print "Content-type: text/plain; charset=utf-8\r\n\r\nHARDCORE DEBUG:\n"
#import cgitb;cgitb.enable()

import os

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "PyLucid.settings"

def traceback_end():
    """
    Print out a traceback and terminate with sys.exit()
    """
    print
    print "-"*80
    import sys
    print "Python v%s" % sys.version
    print "-"*80
    try:
        import sys, traceback
        print traceback.format_exc()
    except Exception, e:
        print "Error: %s" % e
    sys.exit()


try:
    from PyLucid.settings import DEBUG, INSTALL_HELP_URL
except Exception, err:
    print "Content-type: text/plain; charset=utf-8\r\n\r\n"
    print "PyLucid - Low-Level-Error!"
    print
    print "Can't import 'settings':", err
    print
    if os.path.isfile("PyLucid/settings.py"):
        print "Note: './PyLucid/settings.py' exist"
    else:
        print (
            "Error: File './PyLucid/settings.py' doesn't exist!\n"
            "You must rename './PyLucid/settings-example.py'"
            " to './PyLucid/settings.py'"
        )
    print
    print "You must setup your own 'settings.py' for your environment!"
    traceback_end()


if DEBUG:
    """
    Redirect all write to stdout+stderr in DEBUG mode.
    """
    import sys, cgi, inspect

    class BaseOut(object):
        """
        Base class for HeaderChecker and StdErrorHandler
        -global header_send variable
        """
        def __init__(self, out):
            self.out = out
            self.oldFileinfo = ""
            self.header_send = False

        def _get_fileinfo(self):
            """
            Append the fileinfo: Where from the announcement comes?
            """
            try:
                self_basename = os.path.basename(__file__)
                if self_basename.endswith(".pyc"):
                    # cut: ".pyc" -> ".py"
                    self_basename = self_basename[:-1]

                for stack_frame in inspect.stack():
                    # go forward in the stack, to outside of this file.
                    filename = stack_frame[1]
                    lineno = stack_frame[2]
                    if os.path.basename(filename) != self_basename:
                        break

                filename = "...%s" % filename[-25:]
                fileinfo = "%-25s line %3s" % (filename, lineno)
            except Exception, e:
                fileinfo = "(inspect Error: %s)" % e

            return fileinfo

        def send_info(self):
            """
            Write information about the file and line number, from which the
            message comes from.
            """
            fileinfo = self._get_fileinfo()

            if fileinfo != self.oldFileinfo:
                # Send the fileinfo only once.
                self.oldFileinfo = fileinfo
                self.out.write(
                    "<br />[stdout/stderr write from: %s]\n" % fileinfo
                )

        def isatty(self):
            return False
        def flush(self):
            pass

    HEADERS = ("content-type:", "status: 301")#, "status: 200")
    class HeaderChecker(BaseOut):
        """
        Very slow! But in some case very helpfully ;)
        Check if the first line is a html header. If not, a header line will
        be send.
        """
        def check(self, txt):
            txt_lower = txt.lower()
            for header in HEADERS:
                if txt_lower.startswith(header):
                    return True
            return False

        def write(self, *txt):
            txt = " ".join([i for i in txt])
            if self.header_send:
                # headers was send in the past
                pass
            elif self.check(txt) == True:
                # the first Line is a header line -> send it
                self.header_send = True
            else:
                self.wrong_header_info()
                txt = cgi.escape(txt)

            self.out.write(txt)

        def wrong_header_info(self):
            self.out.write("Content-type: text/html; charset=utf-8\r\n\r\n")
            self.out.write("Wrong Header!!!\n")
            self.header_send = True
            self.send_info()

    class StdErrorHandler(BaseOut):
        """
        redirects messages from stderr to stdout.
        Sends a header, if the header were not already sent.
        """
        def write(self, *txt):
            txt = " ".join([i for i in txt])
            if not self.header_send:
                self.out.write("Content-type: text/html; charset=utf-8\r\n\r\n")
                self.out.write("Write to stderr!!!\n")
                self.header_send = True

            self.send_info()
            self.out.write("<pre>%s</pre>" % txt)

    old_stdout = sys.stdout
    sys.stdout = HeaderChecker(old_stdout)
    sys.stderr = StdErrorHandler(old_stdout)
#_____________________________________________________________________________


# Add a custom Python path, you'll want to add the parent folder of
# your project directory. (Optional.)
#BASE_PATH = os.path.abspath(os.path.dirname(__file__))
#sys.path.insert(0, BASE_PATH)

# Switch to the directory of your project. (Optional.)
# os.chdir("/home/user/django/PyLucid/")

try:
    #~ from django.core.servers.cgi import runcgi
    # Normaly the cgi_server.py should be saved in dajngo/core/servers
    # But we used svn:externals to include the django source ;)
    from cgi_server import runcgi
except Exception, e:
    print "Content-type: text/plain; charset=utf-8\r\n\r\n"
    print "<h1>Error:</h1><h2>Can't import the CGI Server:</h2>"
    print "<h3>%s</h3>" % e
    traceback_end()

# Run PyLucid for one request:
try:
    runcgi()
except Exception, e:
    print "Content-type: text/plain; charset=utf-8\r\n\r\n"
    print "Low-Level-Error:", e
    print
    print "-"*80
    print
    print "Have you installed PyLucid?"
    print
    print "If not, follow the instruction here:"
    print INSTALL_HELP_URL
    print
    print "Note:"
    print "If you will go into the _install section, you must temporaly"
    print "deactivate some middlewares in your settings.py:"
    print
    print "Edit the MIDDLEWARE_CLASSES data and deactivate:"
    print " - django.contrib.sessions.middleware.SessionMiddleware"
    print " - django.contrib.auth.middleware.AuthenticationMiddleware"
    print
    print "After 'syncdb' the needed tables created and you must activate the"
    print "middleware classes!"

    traceback_end()