# coding: utf-8

"""
    PyLucid extrahead context middleware
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Stores extra html head content via PyLucid context middleware.
    It's used by pylucid.defaulttags.extraheadBlock.
    
    PyLucid plugins should use {% extrahead %} block tag in plugin template for
    insert e.g. CSS/JS file links into html head.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

__version__= "$Rev:$"

import os
import inspect

from django.conf import settings


FILEPATH_SPLIT = "pylucid_project"

SKIP_MODULES = [
    os.path.join("django", "template"),
    os.path.join("django", "shortcuts"),
    os.path.join("extrahead", "context_middleware")
]

DEBUG_INFO = """\
<!-- extrahead from %(fileinfo)s - START -->
%(content)s
<!-- extrahead from %(fileinfo)s - END -->"""


class ContextMiddleware(object):
    """
    Simple store extra html head content from plugins.
    """
    def __init__(self, request, context):
        self.request = request
        if settings.DEBUG:
            # Turn debug mode in JavaScript on
            self.data = DEBUG_INFO % {
                "fileinfo": os.path.basename(__file__),
                "content": '<script type="text/javascript">var debug=true;log("debug is on");</script>'
            }
            self.data += "\n" 
        else:
            self.data = ""
        
    def add_content(self, content):
        content = content.strip()
        if settings.DEBUG:
            # Add debug info around content.
            fileinfo = self._get_fileinfo()
            content = DEBUG_INFO % {"fileinfo": fileinfo, "content": content}
            
        self.data += content + "\n"
        
    def _add_pagetree_headfiles(self):
        pagetree = self.request.PYLUCID.pagetree
        design = pagetree.design
        
        headfiles = design.headfiles.all()
        
        headfilelinks = []
        for headfile in headfiles:
            # Get a instance from pylucid.system.headfile.HeadfileLink():
            headfilelink = headfile.get_headfilelink()
            head_tag = headfilelink.get_head_tag()
            headfilelinks.append(head_tag)
        
        self.add_content("\n".join(headfilelinks))
        
    def render(self):
        self._add_pagetree_headfiles()
        return self.data
    
    def _get_fileinfo(self):
        """
        return fileinfo: Where from the announcement comes?
        """
        def skip(filepath):
            for ignore_path in SKIP_MODULES:
                if ignore_path in filepath:
                    return True
            return False
        
        try:    
            fileinfo = []
            step = 0
            for stack_frame in inspect.stack():
                filepath = stack_frame[1]              
                lineno = stack_frame[2]

                if skip(filepath) or FILEPATH_SPLIT not in filepath:
                    continue
                
                filepath = "..." + filepath.split(FILEPATH_SPLIT,1)[1]
                
                fileinfo.append("%s line %s" % (filepath, lineno))
                if step>=1:
                    break
                step += 1
            return " | ".join(fileinfo)
        except Exception, e:
            return "(inspect Error: %s)" % e
