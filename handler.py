#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
This will be a central handler to let PyLucid
wort with mod_python, fcgi and cgi with only
change the config.py and the server configuration
"""

import cgitb;cgitb.enable()
import sys
import config

try:
    from PyLucid.system.exceptions_LowLevel import CGI_Error, CGI_main_info
except Exception, e:
    msg = "Can't import PyLucid.system.exceptions_LowLevel.CGI_Error: %s" % e
    print "Content-type: text/html; charset=utf-8\r\n\r\n"
    print "<h2>%s</h2>" % msg
    raise ImportError(msg)


# Colubrid Debugger
try:
    from colubrid.debug import DebuggedApplication
except Exception, e:
    raise CGI_Error(
        e, "Can't import colubrid.debug.DebuggedApplication!"
    )

# Backport for some Python v2.4 features (subprocess.py)
sys.path.insert(0,"PyLucid/python_backports")


def handler_config():
    env = ''
        
    if config.config["environment"] == "cgi":
        # CGI-Handler
        try:
            from wsgiref.handlers import CGIHandler
        except Exception, e:
            # ToDo: better error handling
            raise CGI_Error(e, "Can't import wsgiref-CGI-handler or our CGI-Exceptions")
        
        return CGIHandler
            
    elif config.config["environment"] == "mod_python":
        # ToDo: let us make a mod_python Handler
        pass
        
    elif config.config["environment"] == "fcgi":
        # ToDo: let us integrate a FastCGI Handler 
        pass
    
    else:
        # ToDo: create a exception
        pass

handler = handler_config()

if __name__ == "__main__":
    try:
        # with 'debugged application':
        app = handler_config.DebuggedApplication('PyLucid_app:app')
    except Exception, e:
        raise CGI_Error(e, "Can't init DebuggedApplication!")

    try:
        # NOTE: every handler should support that...
        handler.run(app)
    except Exception, e:
        # NOTE: unimplementated... every Handler should have
        #         his own Exception - if can run correctly
        raise Handler_Exception(e, "Can't run the Handler!")

else:
    # Do we need this now?
    CGI_main_info()

