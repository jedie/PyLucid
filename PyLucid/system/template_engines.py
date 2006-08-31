#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Einheitliche Schnittstelle zu den Templates Engines
"""

__version__="0.1"

__history__="""
v0.1
    - erste Version
"""

__todo__ = """
Muß umgebaut werden, sodas man auch eine get-Methode benutzten kann.
    z.B. für den RSS Generator!
"""

import sys, os


from PyLucid.system.exceptions import *


def render_jinja(template, context):
    """
    Ist als normale Funktion ausgelagert, damit sie auch während der _install
    Phase benutzt werden kann...
    """
    import jinja

    # FIXME: jinja.loader.load() wandelt immer selber in unicode um und
    # mag deswegen kein unicode, also wandeln wir es in einen normale
    # String :(
    template = str(template)

    t = jinja.Template(template, jinja.StringLoader())#, trim=True)
    c = jinja.Context(context)
    content = t.render(c)

    return content



class TemplateEngines(object):

    # Pfad zum aktuellen Template auf der Platte, für Module, die bei der
    # installation interne Seiten nutzten wollen:
    template_path = None

    def __init__(self, request, response):
        self.response = response

        # Shorthands
        self.environ    = request.environ
        self.db         = request.db
        self.runlevel   = request.runlevel
        self.render     = request.render
        self.page_msg   = response.page_msg
        self.addCode    = response.addCode

    def write(self, internal_page_name, context):
        try:
            internal_page_data = self.get_internal_page_data(
                internal_page_name
            )
        except InternalPageNotFound, e:
            import inspect
            stack = inspect.stack()[1]
            msg = (
                "Internal page '%s' not found (from '...%s' line %s): %s"
            ) % (internal_page_name, stack[1][-30:], stack[2], e)
            raise KeyError(msg)

        engine = internal_page_data["template_engine"]
        if engine == "string formatting":
            self.render_stringFormatting(
                internal_page_name, internal_page_data, context
            )
        elif engine == "jinja":
            content = internal_page_data["content_html"]
            content = render_jinja(content, context)
            self.response.write(content)
        else:
            msg = "Template Engine '%s' not implemented!" % engine
            raise NotImplemented, msg

        # CSS/JS behandeln:
        self.addCSS(internal_page_data["content_css"], internal_page_name)
        self.addJS(internal_page_data["content_js"], internal_page_name)

    def get(self, internal_page_name, context):
        """
        FIXME!!!!
        """
        internal_page_data = self.get_internal_page_data(
            internal_page_name
        )
        content = internal_page_data["content_html"]
        content = render_jinja(content, context)
        return content

    def get_internal_page_data(self, internal_page_name):
        if self.runlevel.is_install():
            # Beim installieren holen wir uns die Daten direkt von der Platte
            return self.get_internal_page_data_from_disk(internal_page_name)
        else:
            return self.get_internal_page_data_from_db(internal_page_name)
            # Der Normalfall, die Daten werden aus der DB geholt


    def get_internal_page_data_from_db(self, internal_page_name):
        try:
            return self.db.get_internal_page_data(internal_page_name)
        except IndexError, e:
            raise InternalPageNotFound, e

    def get_internal_page_data_from_disk(self, internal_page_name):
        if self.template_path == None:
            msg = (
                "template_path for internal page '%s' not set by module!"
            ) % internal_page_name
            raise RuntimeError, msg

        cfg_package = self.template_path[:]
        module_name = "%s_cfg" % self.template_path[-1]
        cfg_package = ".".join(cfg_package)

        cfg_module = __import__(
            "%s.%s" % (cfg_package, module_name),
            {}, {}, [module_name]
        )
        module_manager_data = cfg_module.module_manager_data

        method_cfg = module_manager_data[internal_page_name]
        try:
            internal_page_info = method_cfg["internal_page_info"]
        except KeyError, e:
            raise KeyError, (
                "No internal_page_info found for internal page %s"
            ) % internal_page_name

        internal_page_data = {
            "template_engine": internal_page_info["template_engine"],
            "markup": internal_page_info["markup"],
        }

        html_content = self.readContentFile(internal_page_name, "html")

        internal_page_data["content_html"] = html_content

        try:
            content = self.readContentFile(internal_page_name, "css")
        except InternalPageNotFound:
            content = ""
        internal_page_data["content_css"] = content

        try:
            content = self.readContentFile(internal_page_name, "js")
        except InternalPageNotFound:
            content = ""
        internal_page_data["content_js"] = content

        return internal_page_data


    def readContentFile(self, internal_page_name, ext):
        def get_path(internal_page_name, ext):
            template_path = self.template_path[:] # Kopie der Liste
            #~ template_path.insert(0, self.environ["DOCUMENT_ROOT"])
            template_path.append("%s.%s" % (internal_page_name, ext))
            template_path = os.sep.join(template_path)
            return template_path

        file_path = get_path(internal_page_name, ext)
        if not os.path.isfile(file_path):
            raise InternalPageNotFound, (
                "file '%s' not found!"
            ) % file_path

        f = file(file_path, "rU")
        content = f.read()
        f.close()

        return content

    def addCSS(self, content_css, internal_page_name):
        """
        Zusätzlicher Stylesheet Code für interne Seite behandeln
        """
        if content_css=="":
            return

        #~ tag = '<style type="text/css">\n%s\n</style>\n'
        tag = (
            '<style type="text/css">\n'
            '/* <![CDATA[ */\n'
            '/* additional stylesheets from internal page "%s" */\n'
            '%s\n'
            '/* ]]> */\n</style>\n'
        )
        content_type = "Stylesheet"
        self.add(content_css, tag, content_type, internal_page_name)

    def addJS(self, content_js, internal_page_name):
        """
        Zusätzlicher JavaScript Code für interne Seite behandeln
        """
        if content_js=="":
            return

        #~ tag = '<script type="text/javascript">\n%s\n</script>\n'
        tag = (
            '<script type="text/javascript">\n'
            '/* <![CDATA[ */\n'
            '/* additional javascript from internal page "%s" */\n'
            '%s\n'
            '/* ]]> */\n</script>\n'
        )
        content_type = "JavaScript"
        self.add(content_js, tag, content_type, internal_page_name)

    def add(self, code, tag, content_type, internal_page_name):
        """
        Fügt den Code an response.addCode an
        """
        try:
            code = code.encode("utf8")
        except UnicodeError, e:
            msg = (
                "UnicodeError in %s add data for internal page '%s'"
                " (Error: %s)"
            ) % (content_type, internal_page_name, e)
            self.page_msg(msg)
            code = code.encode("utf8", "replace")

        # Tag anwenden
        code = tag % (internal_page_name, code)

        self.addCode.add(code)


    def render_stringFormatting(self, internal_page_name, internal_page_data, context):
        content = internal_page_data["content_html"]

        content = content % context

        try:
            a=1#content = content % context
        except UnicodeError, e:
            self.page_msg("UnicodeError: Can't render internal page: %s" % e)
            self.page_msg("(Try to go around.)")
            try:
                for k,v in context.iteritems():
                    try:
                        context[k] = v.encode("utf_8", 'replace')
                    except Exception: # z.B. bei Zahlen
                        pass

                content = content.encode("utf_8", 'replace')
                content = content % context
                self.response.write(content)
            except:
                self.response.write(
                    "<h4>Can't go around the UnicodeError!</h4>"
                )
                if self.preferences["ModuleManager_error_handling"] != True:
                    raise
        except Exception, e:
            self.page_msg("Error information:")

            s = self.tools.Find_StringOperators(content)
            if s.incorrect_hit_pos != []:
                self.page_msg(" -"*40)
                self.page_msg("There are incorrect %-chars in the internal_page:")
                self.page_msg("Text summary:")
                for line in s.get_incorrect_text_summeries():
                    self.page_msg(line)
                self.page_msg(" -"*40)

            l = s.correct_tags
            # doppelte Einträge löschen (auch mit Python >2.3)
            content_placeholder = [l[i] for i in xrange(len(l)) if l[i] not in l[:i]]
            content_placeholder.sort()
            self.page_msg("*** %s content placeholder:" % len(content_placeholder))
            self.page_msg(content_placeholder)

            l = context.keys()
            given_placeholder = [l[i] for i in xrange(len(l)) if l[i] not in l[:i]]
            given_placeholder.sort()
            self.page_msg("*** %s given placeholder:" % len(given_placeholder))
            self.page_msg(given_placeholder)

            diff_placeholders = []
            for i in content_placeholder:
                if (not i in given_placeholder) and (not i in diff_placeholders):
                    diff_placeholders.append(i)
            for i in given_placeholder:
                if (not i in content_placeholder) and (not i in diff_placeholders):
                    diff_placeholders.append(i)

            diff_placeholders.sort()
            self.page_msg("*** placeholder diffs:", diff_placeholders)

            raise Exception(
                "%s: '%s': Can't fill internal page '%s'. \
                *** More information above in page message ***" % (
                    sys.exc_info()[0], e, internal_page_name,
                )
            )

        content = self.render.apply_markup(
            content, internal_page_data["markup"]
        )

        self.response.write(content)



class InternalPageNotFound(Exception):
    """ Die Interne Seite wurde in der DB nicht gefunden """
    pass
