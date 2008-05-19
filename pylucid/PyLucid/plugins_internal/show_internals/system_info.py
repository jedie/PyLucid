# -*- coding: utf-8 -*-

"""
    PyLucid Show Internals - System Info
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2005-2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

__version__= "$Rev$"


import sys, os, locale, subprocess

from PyLucid.tools.subprocess2 import Subprocess2
from PyLucid.system.BasePlugin import PyLucidBasePlugin

#______________________________________________________________________________
class PyLucidInfo(PyLucidBasePlugin):
    """
    information around PyLucid
    """
    def display_all(self):
        self.response.write("<hr>")
        self.PyLucid_info()
        self.envion_info()


    def PyLucid_info(self):
        self.response.write("<h3>PyLucid environ information</h3>")

        self.response.write('<fieldset id="system_info">')
        self.response.write(
            '<legend>'
            '<a href="http://www.pylucid.org/_goto/62/self-URLs/">'
            'PyLucid["URLs"]</a>:'
            '</legend>'
        )
        self.response.write("<pre>")

        data = [(len(v), k, v) for k,v in self.URLs.items()]

        max_len = max([len(k) for k in self.URLs])
        line = "%%%ss: '%%s'\n" % max_len

        for _,k,v in sorted(data):
            self.response.write(line % (k,v))

        self.response.write("</pre>")
        self.response.write("</fieldset>")


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



#______________________________________________________________________________
class PythonInfo(PyLucidBasePlugin):
    """
    information around the Python installation
    """
    def display_all(self):
        self.response.write("<hr>")
        self.python_info()
        self.encoding_info()


    def python_info(self):
        self.response.write("<h3>Python info</h3>")
        self.response.write('<dl id="python_info">')
        self.response.write("<dt>sys.version:</dt>")
        self.response.write("<dd>Python v%s</dd>" % sys.version)

        self.response.write("<dt>sys.path:</dt>")
        for i in sys.path:
            self.response.write("<dd>%s</dd>" % i)

        self.response.write("<dt>sys.modules:</dt>")
        self.response.write("<table>")
        no = 0
        for module_name, module in sorted(sys.modules.iteritems()):
            no += 1

            doc = getattr(module, "__doc__", None)
            if doc:
                doc = doc.strip().split("\n", 1)[0]
            else:
                doc = "[no __doc__ available]"

            file_info = getattr(module, "__file__", repr(module))

            self.response.write("<tr>\n")
            self.response.write("\t<td>%s</td>\n" % no)
            self.response.write("\t<td>%s</td>\n" % module_name)
            self.response.write("\t<td>%s</td>\n" % doc)
            self.response.write("\t<td>%s</td>\n" % file_info)
            self.response.write("</tr>\n")
        self.response.write("</table>")

        self.response.write("</dl>")


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



#______________________________________________________________________________
class SystemInfo(PyLucidBasePlugin):
    """
    generic system information
    """
    def display_all(self):
        self.response.write("<hr>")
        self.system_info()
        self.cmd_info()
        self.proc_info()


    def system_info(self):
        self.response.write("<h3>system info</h3>")

        self.response.write('<dl id="system_info">')
        if hasattr(os,"uname"): # Nicht unter Windows verfügbar
            self.response.write("<dt>os.uname():</dt>")
            self.response.write("<dd>%s</dd>" % " - ".join( os.uname() ))

        try:
            loadavg = os.getloadavg()
            loadavg = ", ".join([str(round(i,2)) for i in loadavg])
            self.response.write("<dt>load average:</dt>")
            self.response.write("<dd>%s</dd>" % loadavg)
        except OSError:
            # Not available
            pass

        self.response.write("</dl>")


    def proc_info(self):
        """
        Dispaly some proc files
        """
        files = ["/proc/meminfo", "/proc/stat", "/proc/loadavg"]

        self.response.write("<h3>proc info</h3>")

        self.response.write('<dl id="system_info">')
        for proc_file in files:
            self.response.write("<dt>'%s':</dt>" % proc_file)
            try:
                f = file(proc_file, "r")
            except Exception, e:
                self.response.write("<dd>Error: %s</dd>" % e)
            else:
                for line in f:
                    self.response.write("<dd>%s</dd>" % line)
                f.close()
        self.response.write("</dl>")


    def cmd_info(self):
        """
        Use some commandline programms and display the output
        """
        commands = (
            "w", "df -T -h", "free -m",
            "ssh-keygen -l -f /etc/ssh/ssh_host_rsa_key.pub"
        )
        for command in commands:
            self.response.write(
                """<fieldset><legend>%s</legend>""" % command
            )
            try:
                p = Subprocess2(command,
                    stdout=subprocess.PIPE,
                    shell = True,
                    timeout = 1
                )
            except Exception, e:
                self.response.write("Error: %s" % e)
            else:
                if not p.killed:
                    # read only if process ended normaly, otherwise it blocked!
                    msg = "<pre>%s</pre>" % p.process.stdout.read()
                else:
                    msg = "Proecess was killed. Returncode: %s" % (
                        p.process.returncode
                    )
                self.response.write(msg)

            self.response.write("</fieldset>")








