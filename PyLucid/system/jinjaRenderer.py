#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Eine kleine jinja Hilfsklasse
"""

#~ from jinja import Template, Context, FileSystemLoader
import jinja

class jinjaRenderer:
    def __init__(self, request, templateDir="templates", suffix=".html"):
        self.request        = request
        self.templatename   = templatename
        self.templateDir    = templateDir
        self.suffix         = suffix

        # Shorthands
        self.page_msg   = self.response.page_msg

    def render(self, templatename, context):
        #~ try:
            #~ loader = CachedFileSystemLoader('templates', suffix=suffix, charset='utf-8')
            #~ template = Template(templatename, loader)
        #~ except:# EOFError, ImportError:
            #~ self.response.write("<small>(jinja FileSystemLoader fallback)</small>")

        loader = FileSystemLoader(self.templateDir, suffix=self.suffix, charset='utf-8')
        template = Template(self.templatename, loader)

        context = Context(self.request.context, charset='utf-8')

        content = template.render(context)
        if isinstance(content, unicode):
            content = content.encode("utf-8")
        else:
            self.page_msg("jinja content not unicode!")

        return content