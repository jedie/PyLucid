#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
-Parsen der Seite und wendet das Markup an.
-Schnittstelle zu PyKleur
"""

__version__="0.2"

__history__="""
v0.2
    - Neu: highlight() - Schnittstelle zu PyKleur
v0.1.4
    - apply_markup kommt mit markup id oder richtigen namen klar
v0.1.3
    - textile Parser erhält nun auch die PyLucid-Objekt. page_msg ist
        hilfreich zum debuggen des Parsers ;)
v0.1.2
    - Bug 1297263:
        "Can't use textile-Markup (maximum recursion limit exceeded)":
        Nun wird zuerst das Markup angewendet und dann erst die lucidTag's
        aufgelöst
v0.1.1
    - parser.handle_function(): toleranter wenn kein String vom Modul zurück
        kommt
    - Versionsnummer geändert
v0.1.0
    - Erste Version: Komplett neugeschrieben. Nachfolge vom pagerender.py
"""

__todo__ = """
in apply_markup sollte nur noch mit markup IDs erwartet werden. Solange aber
die Seiten keine IDs, sondern die richtigen Namen verwenden geht das leider
noch nicht :(
"""

import sys, cgi, re, time



class render(object):

    # http://trac.pocoo.org/browser/pocoo/trunk/pocoo/pkg/highlight/components.py
    PyKleurLexers = {
        'python':       ('Python',                  'py', "PythonLexer"),
        'py':           ('Python',                  'py', "PythonLexer"),
        'php':          ('PHP',                     'php', "PhpLexer"),
        'c':            ('C',                       'c', "CppLexer"),
        'c++':          ('C++',                     'cpp', "CppLexer"),
        'cpp':          ('C++',                     'cpp', "CppLexer"),
        'delphi':       ('Delphi',                  'delphi', "DelphiLexer"),
        'java':         ('Java',                    'java', "JavaLexer"),
        'html':         ('HTML',                    'html', "HtmlLexer"),
        'xml':          ('XML',                     'html', "XmlLexer"),
        'javascript':   ('JavaScript',              'js', "JavascriptLexer"),
        'js':           ('JavaScript',              'js', "JavascriptLexer"),
        'css':          ('Cascading Style Sheets',  'css', "CssLexer"),
        'ini':          ('INI',                     'ini', "IniLexer"),
        'sql':          ('SQL',                     'sql', "SqlLexer"),
    }

    def init2(self, request, response):
        self.request = request
        self.response = response

        #shorthands
        self.session        = request.session
        self.db             = request.db
        self.staticTags     = request.staticTags
        self.preferences    = request.preferences
        self.tools          = request.tools
        self.page_msg       = response.page_msg

    def write_page_template(self):
        """ Baut die Seite zusammen """

        page_id = self.session["page_id"]
        page_data = self.db.get_side_data(page_id)
        self.staticTags.fill_with_page_data(page_data)

        template_data = self.db.side_template_by_id(self.session["page_id"])
        self.response.write(template_data)

    def write_command_template(self):
        # FIXME - Quick v0.7 Patch !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        template_data = self.db.side_template_by_id(self.session["page_id"])
        self.response.write(template_data)

    def get_rendered_page(self, page_id):
        page = self.db.get_content_and_markup(page_id)
        #~ self.page_msg(page)
        content = self.apply_markup(
            content = page["content"],
            markup = page["markup"]
        )
        return content

    def apply_markup(self, content, markup):
        """
        Wendet das Markup auf den Seiteninhalt an
        """
        if markup == "textile":
            # textile Markup anwenden
            if self.preferences["ModuleManager_error_handling"] == True:
                try:
                    from PyLucid.system import tinyTextile
                    out = self.tools.out_buffer()
                    t = tinyTextile.parser(out, self.request, self.response)
                    t.parse(content)
                    return out.get()
                except Exception, e:
                    msg = "Can't use textile-Markup (%s)" % e
                    self.page_msg(msg)
                    return msg
            else:
                from PyLucid.system import tinyTextile
                out = self.tools.out_buffer()
                t = tinyTextile.parser(out, self.request, self.response)
                t.parse(content)
                return out.get()
        elif markup in ("none", "None", None, "string formatting"):
            return content
        else:
            self.page_msg("Markup '%s' not supported yet :(" % markup)
            return content

    #_________________________________________________________________________

    def highlight(self, ext, code, out_object=None):
        """
        Schnittstelle zu PyKleur
        """
        if out_object == None:
            out_object = self.response

        html_fieldset = (
            '<fieldset class="syntax"><legend class="syntax">%s</legend>\n',
            '</fieldset>'
        )
        html_pre = '<pre class="syntax">'
        html_post = "</pre>"

        try:
            legend, ext, lexer_name = self.PyKleurLexers[ext.lower()]
        except KeyError, e:
            # Kein Lexter gefunden
            legend = "%s <small>[no highlight lexer available.]</small>" % ext
            out_object.write(html_fieldset[0] % legend)
            out_object.write(html_pre)
            out_object.write(code)
            out_object.write(html_post)
            out_object.write(html_fieldset[1])
            return

        from pykleur import highlight
        from pykleur.formatters import HtmlFormatter
        from pykleur import highlight, lexers

        lexer = getattr(lexers, lexer_name)
        formatter = HtmlFormatter(pre=html_pre, post=html_post)

        out_object.write(html_fieldset[0] % legend)
        highlight(code, lexer(), formatter, out_object)
        out_object.write(html_fieldset[1])