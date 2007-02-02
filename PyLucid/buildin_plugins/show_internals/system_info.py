#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
show internals - system info

Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

__version__= "$Rev$"


import sys, os, locale

from PyLucid.system.BaseModule import PyLucidBaseModule

class SystemInfo(PyLucidBaseModule):
    def display_all(self):
        self.response.write("<hr>")

        self.PyLucid_info()
        self.system_info()
        self.encoding_info()
        self.envion_info()
        self.colubrid_debug_link()

    #_________________________________________________________________________

    def PyLucid_info(self):
        self.response.write("<h3>PyLucid environ information</h3>")

        self.response.write('<fieldset id="system_info">')
        self.response.write('<legend>PyLucid["URLs"]:</legend>')
        self.response.write("<pre>")
        for k,v in self.URLs.items():
            self.response.write("%15s: '%s'\n" % (k,v))
        self.response.write("</pre>")
        self.response.write("</fieldset>")

        self.response.write('<fieldset id="system_info">')
        self.response.write('<legend>self.i18n.debug():</legend>')
        self.response.write("<pre>")
        self.i18n.debug(response_out=True)
        self.response.write("</pre>")
        self.response.write("</fieldset>")

    #_________________________________________________________________________

    def system_info(self):
        self.response.write("<h3>system info</h3>")

        self.response.write('<dl id="system_info">')
        if hasattr(os,"uname"): # Nicht unter Windows verfügbar
            self.response.write("<dt>os.uname():</dt>")
            self.response.write("<dd>%s</dd>" % " - ".join( os.uname() ))

        self.response.write("<dt>sys.version:</dt>")
        self.response.write("<dd>Python v%s</dd>" % sys.version)

        self.response.write("<dt>sys.path:</dt>")
        for i in sys.path:
            self.response.write("<dd>%s</dd>" % i)

        #~ self.response.write("<dt>config file:</dt>")
        #~ self.response.write("<dd>%s</dd>" % self.config.__file__)

        self.response.write("</dl>")

        #_____________________________________________________________________

        self.cmd_info( "uptime", "uptime" )
        self.cmd_info( "lokal Angemeldete Benutzer", "who -H -u --lookup" )
        self.cmd_info( "disk", "df -T -h" )
        self.cmd_info( "RAM", "free -m" )

    #_________________________________________________________________________

    def envion_info(self):
        self.response.write("<h3>OS-Enviroment:</h3>")
        self.response.write('<dl id="environment">')
        keys = os.environ.keys()
        keys.sort()
        for key in keys:
            value = os.environ[key]
            self.response.write("<dt>%s</dt>" % key)
            self.response.write("<dd>%s</dd>" % value)
        self.response.write("</dl>")

    def colubrid_debug_link(self):
        self.response.write("<h3>Colubrid debug information</h3>")
        # FIXME: Das JS sollte anders eingebunden werden!
        url = self.URLs.actionLink("colubrid_debug")
        self.response.write(
            '<script type="text/javascript">'
            '/* <![CDATA[ */'
            'function OpenInWindow(URL) {'
            '  win1 = window.open('
            'URL, "", "width=1000, height=600, dependent=yes, resizable=yes,'
            ' scrollbars=yes, location=no, menubar=no, status=no,'
            ' toolbar=no");'
            '  win1.focus();'
            '}'
            '/* ]]> */'
            '</script>'
        )
        html = (
            '<a href="%s" onclick="OpenInWindow(this.href); return false"'
            ' title="colubrid debug">'
            'show colubrid debug'
            '</a>'
        ) % url
        self.response.write(html)

    #_________________________________________________________________________

    def encoding_info(self):
        self.response.write("<h3>encoding info</h3>")

        self.response.write('<dl id="system_info">')

        def get_file_encoding(f):
            if hasattr(f, "encoding"):
                return f.encoding
            else:
                return "Error: Object has no .encoding!"

        self.response.write("<dt>sys.stdin.encoding:</dt>")
        self.response.write("<dd>%s</dd>" % get_file_encoding(sys.stdin))

        self.response.write("<dt>sys.stdout.encoding:</dt>")
        self.response.write("<dd>%s</dd>" % get_file_encoding(sys.stdout))

        self.response.write("<dt>sys.stderr.encoding:</dt>")
        self.response.write("<dd>%s</dd>" % get_file_encoding(sys.stderr))


        self.response.write("<dt>sys.getdefaultencoding():</dt>")
        self.response.write("<dd>%s</dd>" % sys.getdefaultencoding())

        self.response.write("<dt>sys.getfilesystemencoding():</dt>")
        try:
            self.response.write("<dd>%s</dd>" % sys.getfilesystemencoding())
        except Exception, e:
            self.response.write("<dd>Error: %s</dd>" % e)

        self.response.write("<dt>locale.getlocale():</dt>")
        self.response.write("<dd>%s</dd>" % str( locale.getlocale() ))

        self.response.write("<dt>locale.getdefaultlocale():</dt>")
        self.response.write("<dd>%s</dd>" % str( locale.getdefaultlocale() ))

        self.response.write("<dt>locale.getpreferredencoding():</dt>")
        try:
            self.response.write("<dd>%s</dd>" % str( locale.getpreferredencoding() ))
        except Exception, e:
            self.response.write("<dd>Error: %s</dd>" % e)

        self.response.write("</dl>")

    #_________________________________________________________________________

    def cmd_info(self, info, command, cwd="/"):
        self.response.write(
            '<fieldset id="system_info"><legend>%s:</legend>' % info
        )
        try:
            process = self.tools.subprocess2(command, cwd, 5)
        except Exception,e:
            self.response.write("Can't get: %s" % e)
        else:
            self.response.write("<pre>%s</pre>" % process.out_data)
        self.response.write("</fieldset>")








