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


# Backport for some Python v2.4 features (subprocess.py)
sys.path.insert(0,"PyLucid/python_backports")


def handler_config():
    env = ''
    try:
        from colubrid.debug import DebuggedApplication
    except Exception, e:
        raise CGI_Error(
            e, "Can't import colubrid.debug.DebuggedApplication!"
        )
        
    if config.config["environment"] == "cgi":
        # CGI-Handler
        try:
            from wsgiref.handlers import CGIHandler
        except Exception, e:
            raise CGI_Error(e, "Can't import wsgiref.handlers.CGIHandler!")
        
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
        app = DebuggedApplication('PyLucid_app:app')
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

