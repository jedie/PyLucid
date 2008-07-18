# -*- coding: utf-8 -*-

"""
    PyLucid Show Internals - System Info
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: 2008-06-05 14:57:04 +0200 (Do, 05 Jun 2008) $
    $Rev: 1634 $
    $Author: JensDiemer $

    :copyleft: 2005-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

__version__= "$Rev: 1634 $"

import os, pprint

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
class DjangoInfo(PyLucidBasePlugin):
    """
    information around PyLucid
    """
    def display_all(self):
        self.response.write("<hr>")
        self.response.write("<h3>Django environ information</h3>")
        self.header_info()
        self.apps_models()
        self.django_info()

    def apps_models(self):
        """
        List of all installed apps and his models.
        """
        from django.db.models import get_apps, get_models

        self.response.write('<fieldset id="system_info">')
        self.response.write(
            '<legend>apps / models list</legend>'
        )
        self.response.write("<ul>")

        apps_info = []
        for app in get_apps():
            self.response.write(
                "<li><strong>%s</strong></li>" % app.__name__
            )
            self.response.write("<ul>")
            for model in get_models(app):
                model_name = model._meta.object_name
                self.response.write(
                    "<li>%s</li>" % model_name
                )
            self.response.write("</ul>")

        self.response.write("</ul>")
        self.response.write("</fieldset>")

    def django_info(self):
        from django.core.management import sql

        self.response.write('<fieldset id="system_info">')
        self.response.write(
            '<legend>existing database tables</legend>'
        )
        self.response.write("<h4>sql.table_names():</h4>")
        self.response.write("<pre>")
        self.response.write("\n".join(sorted(sql.table_names())))
        self.response.write("</pre>")

        self.response.write("<h4>sql.django_table_names():</h4>")
        self.response.write("<pre>")
        self.response.write("\n".join(sorted(sql.django_table_names())))
        self.response.write("</pre>")

        self.response.write("</fieldset>")

    def header_info(self):
        self.response.write('<fieldset id="system_info">')
        self.response.write(
            '<legend>request.META</legend>'
        )
        self.response.write("<pre>")
        self.response.write(pprint.pformat(self.request.META))
        self.response.write("</pre>")

        self.response.write("</fieldset>")