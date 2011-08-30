#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid mod_wsgi dispatcher
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    You should check if the shebang is ok for your environment!
        some examples:
            #!/usr/bin/env python
            #!/usr/bin/env python2.4
            #!/usr/bin/env python2.5
            #!/usr/bin/python
            #!/usr/bin/python2.4
            #!/usr/bin/python2.5
            #!C:\python\python.exe

    This script is for standalone installation, not for virtual environment!

    :copyleft: 2007-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import os
import sys
import time
import traceback
import StringIO


# This must normaly not changes, because you should use a local_settings.py file
os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"


# Low level log file. Only created if the fastCGI app can't start.
LOGFILE = "low_level_wsgi.log"


def low_level_log(msg):
    """ append >msg< into LOGFILE """
    try:
        msg = "%s - %s\n" % (time.ctime()[4:-4], msg)
        f = open(LOGFILE, 'a')
        f.write(msg)
        f.close()
        sys.stderr.write(msg)
    except Exception, err:
        sys.stderr.write("Error, creating %r: %s" % (LOGFILE, err))

#~ low_level_log("startup...")

def run_django_wsgi():
    """
    run the django app with django.core.servers.fastcgi.runfastcgi
    turn flup debug on, if settings.DEBUG is on.
    """
    try:
        from django.conf import settings
    except:
        etype, evalue, etb = sys.exc_info()
        evalue = etype("Can't import 'settings'!")
        raise etype, evalue, etb

    try:
        from django.core.handlers.wsgi import WSGIHandler
    except Exception, err:
        etype, evalue, etb = sys.exc_info()
        evalue = etype("Can't import django stuff: %s" % err)
        raise etype, evalue, etb

    application = WSGIHandler()
    low_level_log("Action 1")
    return application


try:
    application = run_django_wsgi()
except:
    # Catch the traceback and run a minimal wsgi debug application
    low_level_log(traceback.format_exc()) # Write full traceback into LOGFILEdrag

#~ low_level_log("-- END --")

