#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Internationalisierung

Last commit info:
----------------------------------
$LastChangedDate:$
$Rev:$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php

"""

class I18N(object):
    current_lang = "en"

    def __init__(self, request, response):
        self.request    = request
        self.response   = response

        # shorthands
        self.environ        = request.environ
        self.page_msg       = response.page_msg
        self.db             = request.db

        #~ self.runlevel       = request.runlevel
        #~ self.session        = request.session
        #~ self.preferences    = request.preferences
        #~ self.URLs           = request.URLs
        #~ self.log            = request.log
        #~ self.module_manager = request.module_manager
        #~ self.tools          = request.tools
        #~ self.render         = request.render
        #~ self.tag_parser     = request.tag_parser
        #~ self.staticTags     = request.staticTags
        #~ self.templates      = request.templates

        self.setup_current_lang()

    #_________________________________________________________________________

    def setup_current_lang(self):
        self.client_languages = self.get_client_favored_languages()

        if "lang" in self.request.args:
            self.client_languages.insert(0, self.request.args["lang"])

        self.supported_languages = self.db.get_supported_languages()

        for lang in self.client_languages:
            if lang in self.supported_languages:
                self.current_lang = lang
                break

    def get_client_favored_languages(self):
        try:
            language_string = self.environ['HTTP_ACCEPT_LANGUAGE']
        except KeyError:
            return ["en"]

        languages = []
        language_string = language_string.split(',')
        for item in language_string:
            lang = item.split(';', 1)[0]
            lang = lang.lower()
            if lang in languages:
                continue
            languages.append(lang)
            if '-' in lang:
                lang = lang.split('-')[0]
                languages.append(lang)

        return languages

    #_________________________________________________________________________

    def debug(self, response_out=False):

        #~ self.response.debug()
        def out(*txt):
            if response_out:
                self.response.write("%s\n" % " ".join([str(i) for i in txt]))
            else:
                self.page_msg(*txt)

        out("self.client_languages:", self.client_languages)
        out("self.supported_languages:", self.supported_languages)
        out("self.current_lang:", self.current_lang)