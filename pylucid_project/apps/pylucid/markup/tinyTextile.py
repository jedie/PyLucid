# -*- coding: utf-8 -*-

"""
    tinyTextile
    ~~~~~~~~~~~

    PyLucid builtin markup engine. Based on the textile markup.

    ToDo
    ~~~~
    Most parts works well, but the code is very old and process in a stream was
    not the best idea: e.g. sourceode parts doesn't work well, there should be
    exctract/insert before the markup applied. So these engine should be
    complete rewritten.
    other todos:
      * lists are not good indented

    links
    ~~~~~
    http://www.pylucid.org/_goto/5/Markup/
    http://dealmeida.net/en/Projects/PyTextile/
    http://www.solarorange.com/projects/textile/mtmanual_textile2.htm

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate:2008-05-13 18:26:55 +0200 (Di, 13 Mai 2008) $
    $Rev:1561 $
    $Author:JensDiemer $

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


__version__ = "$Rev:1561 $"

import sys, re

from xml.sax.saxutils import escape


class TinyTextileParser:
    def __init__(self, out_obj, page_msg):
        self.out = out_obj
        self.page_msg = page_msg

        # Blockelements
        self.block_rules = self._compile_rules([
            [ # <h1>-Headlines
                r"\Ah(\d)\. (.+)(?usm)",
                r"<h\1>\2</h\1>"
            ],
        ])

        # Inlineelements
        self.inline_rules = self._compile_rules([
            [ # HTML-Escaping
                r"={2,2}(.+?)={2,2}(?usm)",
                self.escaping
            ],
            [ # Kleiner Text - Bsp.: Ich bin ein --kleines-- Wort.
                r"-{2,2}([^-]+?)-{2,2}",
                r"<small>\1</small>"
            ],
            [ # Fettschrift - Bsp.: Das Wort ist in *fett* geschrieben.
                r"\*([^*\n]+?)\*(?uism)",
                r"<strong>\1</strong>"
            ],
            [ # manuell linebreak
                r"\\{2,2}",
                r"<br />"
            ],
            [ # img-Tag - Bsp.: !/Bilder/MeinBild.jpg!
                r'\!([^!\n ]+?)\!(?uis)',
                r'<img src="\1">'
            ],
            [ # Link + LinkText - e.g.: "LinkText":http://www.beispiel.de
              # old link format!
                r'"([^"]+?)":([^\s\<]+)',
                r'<a href="\2">\1</a>'
            ],
            [ # Link + LinkText - e.g.: "LinkText":http://www.beispiel.de
              # new link format - e.g.: [http://domain.dtl link text]
                r'\[([^\s\<]+) (.+?)\]',
                r'<a href="\1">\2</a>'
            ],
            [ # interne PyLucid Links - Bsp.:
              # Das ist ein [[InternerLink]] zur Seite InternerLink ;)
                r'\[\[(.+?)\]\]',
                self.shortcutLink
            ],
            [
                # Links allein im Text
                # Bsp.: Das wird ein Link: http://www.beispiel.de
                r'''
                    (?<!=") # Ist noch kein HTML-Link
                    (?P<url>(http|ftp|svn|irc)://([^\s\<]+))
                    (?uimx)
                ''',
                r'<a href="\g<url>">\g<url></a>'
            ],
            [ # EMails
                r'mailto:([^\s\<]+)',
                r'<a href="mailto:\1">\1</a>'
            ],
        ])

        # Pre-Process Regeln
        self.pre_process_rules = self._compile_rules([
            [ # Text vor einer "*"-Liste mit noch einem \n trennen
                r"""
                    (^[^*\n].+?$) # Text-Zeile vor einer Liste
                    (\n^\*) # Absatz + erstes List-Zeichen
                    (?uimx)
                """,
                r"\1\n\2",
            ],
            [ # Text vor einer "#"-Liste mit noch einem \n trennen
                r"""
                    (^[^#\n].+?$) # Text-Zeile vor einer Liste
                    (\n^\#) # Absatz + erstes List-Zeichen
                    (?uimx)
                """,
                r"\1\n\2",
            ],
            [ # insert \n before and after a "|"-Table
                r"(?ms)(^\|.*?\|\n(?!\|))", # match the complete table block
                r"\n\1\n",
            ],
            [
                # Text *vor* einem <pre>, <python> oder <code> Block mit noch
                # einem \n trennen
                r"\n(?P<tag><(pre|python|code[^>]*?)>)\n",
                r"\n\n\g<tag>\n",
            ],
            [
                # Text *nach* einem <pre>, <python> oder <code> Block mit noch
                # einem \n trennen
                r"\n(?P<tag></(pre|python|code)>)\n",
                r"\n\g<tag>\n\n",
            ],
#            [
#                "(?ms)(<(pre|python|code[^>]*?)>.*?</(pre|python|code)>)",
#                r"\n\1\n"
#            ]
        ])

        self.area_rules = (
            [
                "==", "==",
                self.escape_area_start, self.escape_area, self.escape_area_end
            ],
            [
                "<pre>", "</pre>",
                self.pre_area, self.pre_area, self.pre_area
            ],
            [
                "<python>", "</python>",
                self.python_area_start, self.python_area, self.python_area_end
            ],
            [
                "<code", "</code>",
                self.code_area_start, self.code_area, self.code_area_end
            ],
        )

    def _compile_rules(self, rules):
        "Kompliliert die RE-Ausdrücke"
        for rule in rules:
            rule[0] = re.compile(rule[0])
        return rules

    def parse(self, txt):
        "Parsed den Text in's out_obj"
        txt = self.pre_process(txt)
        self.make_paragraphs(txt)

    def escaping(self, matchobj):
        return escape(matchobj.group(1))

    def shortcutLink(self, matchobj):
        shortcut = matchobj.group(1)
        url = "/%s/" % shortcut.strip("/")
        link = '<a href="%s">%s</a>' % (
            url, shortcut
        )
        return link

    def pre_process(self, txt):
        "Vorab Verarbeitung des Textes"

        # Zeilenenden vereinheitlichen
        txt = txt.replace("\r\n", "\n").replace("\r", "\n")

        # Leerzeilen vorn und hinten abschneiden
        txt = txt.strip()

        # Preprocess rules anwenden
        for rule in self.pre_process_rules:
            #~ self.page_msg(rule)
            #~ self.page_msg(txt)
            txt = rule[0].sub(rule[1], txt)
            #~ self.page_msg(txt)

        return txt

    def make_paragraphs(self, txt):
        """
        Verarbeitung des Textes.
        Wendet Blockelement-Regeln und Inlineelement-Regeln an.
        """
        blocks = re.split("\n{2,}", txt)
        #~ self.page_msg(escape(str(blocks)))
        current_area = None
        for block in blocks:
            current_area = self.handle_areas(block, current_area)
            if current_area != None:
                # Wir sind in einer Area und der Block wurde schon abgehandelt
                continue

            block = block.strip()
            if len(block) == 0:
                continue

            #~ if self.is_html.findall(block) != []:
            if block[0] == "<":
                # Der Block scheint schon HTML-Code zu sein
                self.out.write("%s\n" % block)
                #~ self.page_msg("Is HTML:", escape(block))
                continue

            # inline-rules Anwenden
            for inlinerule in self.inline_rules:
                block = inlinerule[0].sub(inlinerule[1], block)

            # Block-rules Anwenden
            self.blockelements(block)

    #_________________________________________________________________________
    # Areas

    def handle_areas(self, block, current_area):
        """
        Areas anhandeln
        """
        #~ self.page_msg(current_area, "--", escape(block))

        def handle_end(current_area, block):
            if block.endswith(current_area[1]):
                # Die aktuelle Area ist zuende
                inner_block = block[:-len(current_area[1])].rstrip()
                # Erstmal die restlichen Daten verabeiten
                current_area[3](inner_block)

                current_area[4](current_area[1]) # Endmethode aufrufen
                return False

        if (current_area != None) and (current_area != False):
            # Wir sind gerade in einer area

            if handle_end(current_area, block) == False:
                # Ende erreicht
                return False

            # Methode die für die area zuständig ist aufrufen
            current_area[3]("\n%s\n" % block)

            # In der area bleiben
            return current_area

        #~ self.page_msg("handle:", escape(block))
        for current_area in self.area_rules:
            #~ self.page_msg(escape(current_area[0]), block)
            if block.startswith(current_area[0]): # Start einer neuen area
                area_tag = current_area[0]

                # Area-Start-Methode aufrufen
                current_area[2](area_tag)

                rest_block = block[len(area_tag):]
                try:
                    if rest_block[0] == "\n":
                        # Evtl. vorhandene Leerzeile ignorieren
                        rest_block = rest_block[1:]
                except IndexError:
                    # Es ist ein Leerzeichen zwischem Tag und Inhalt
                    # (kommt selten vor)
                    pass

                if handle_end(current_area, rest_block) == False:
                    # Das Ende schon erreicht
                    return False

                # Das Ende ist noch nicht erreicht, also
                # den Restlichen Block durch die normale Methode jagen
                current_area[3](rest_block)

                # In-der-Area-Methode "merken"
                return current_area

        # Wir sind nicht in einer Area
        return None

    #_________________________________________________________________________

    def escape_area_start(self, block):
        self.escape_area_first_line = True
        pass

    def escape_area(self, block):
        if self.escape_area_first_line == True:
            block = block.strip()
            self.escape_area_first_line = False

        block = block.splitlines()
        block = "".join(["%s<br />\n" % escape(line) for line in block])
        self.out.write(block)

    def escape_area_end(self, block):
        pass

    #_________________________________________________________________________

    def pre_area(self, block):
        self.out.write(block + "\n")

    #_________________________________________________________________________

    def python_area_start(self, block):
        """
        Python-Source-Code area
        """
        self.sourcecode_data = []

    def python_area(self, block):
        self.sourcecode_data.append(block)
        if not block.endswith("\n"):
            self.sourcecode_data.append("\n")

    def python_area_end(self, dummy):
        self.hightlight("python", self.sourcecode_data)

    #_________________________________________________________________________

    def code_area_start(self, block):
        """
        Sourcecode mit pygments
        """
        self.first_sourcecode_block = True
        self.sourcecode_type = None
        self.sourcecode_data = []

    def code_area(self, block):
        if self.first_sourcecode_block:
            # Aus der ersten Zeile den Typ des Sourcecodes ermitteln:
            # <code=sql> oder <code=.sh> oder <code>
            self.first_sourcecode_block = False
            code_type, block = block.split(">", 1)
            self.sourcecode_type = code_type.lstrip("=.")

        self.sourcecode_data.append("\n%s\n" % block)

    def code_area_end(self, dummy):
        """
        Wir sind, beim Endtag angekommen, dann zeigen wir mal den
        sourcecode... :)
        """
        self.hightlight(self.sourcecode_type, self.sourcecode_data)

    #_________________________________________________________________________

    def table(self, text):
        result = ""
        for line in text.splitlines():
            line = line.strip("|").split("|")
            result_line = ""
            for cell in line:
                if cell.startswith("="):
                    tag = "th"
                    cell = cell[1:]
                else:
                    tag = "td"
                cell = cell.strip()
                result_line += "\t<%(t)s>%(c)s</%(t)s>\n" % {
                    "t": tag, "c": cell
                }

            result += "<tr>\n%s</tr>\n" % result_line

        result = '<table>\n%s</table>\n' % result
        self.out.write(result)

    #_________________________________________________________________________

    def hightlight(self, source_type, code_lines):
        """
        Display Sourcecode.
        Try to use pygments, if exists.
        """
#        self.page_msg("Source type: '%s'" % source_type)

        code = "".join(code_lines)
        code = code.strip()

        from pylucid_project.apps.pylucid.markup.hightlighter import make_html
        html = make_html(code, source_type, django_escape=True)
        self.out.write(html)

    #_________________________________________________________________________

    def blockelements(self, block):
        "Anwenden der Block-rules. Formatieren des Absatzes"

        if block[0] in ("*", "#"):
            # Aktueller Block ist eine Liste
            self.build_list(block)
            return

        if block[0] == "|":
            # current block is a table
            self.table(block)
            return

        for rule in self.block_rules:
            txt, count = rule[0].subn(rule[1], block)

            if count != 0:
                # Ein Blockelement wurde gefunden
                self.out.write("%s\n" % txt)
                return

        # Kein Blockelement gefunden -> Formatierung des Absatzes
        block = block.strip().replace("\n", "<br />\n")
        self.out.write("<p>%s</p>\n" % block)

    def build_list(self, listitems):
        "Erzeugt eine Liste aus einem Absatz"

        def spacer(deep):
            return " " * (deep * 3)

        def write(number, tag, spacer):
            for i in range(number):
                self.out.write(spacer + tag)

        deep = 0
        for item in re.findall("([\*#]+) (.*)", listitems):
            currentlen = len(item[0])
            if item[0][0] == "*":
                # normale Aufzählungsliste
                pre_tag = "<ul>\n"
                post_tag = "</ul>\n"
            else:
                # Nummerierte Liste
                pre_tag = "<ol>\n"
                post_tag = "</ol>\n"

            if currentlen > deep:
                write(currentlen - deep, pre_tag, spacer(deep))
                deep = currentlen
            elif currentlen < deep:
                write(deep - currentlen, post_tag, spacer(deep))
                deep = currentlen

            self.out.write(
                "%s<li>%s</li>\n" % (spacer(deep), item[1])
            )

        for i in range(deep):
            self.out.write(post_tag)

if __name__ == "__main__":
    # Quick test
    from tests.utils.FakeRequest import get_fake_context
    fake_context = get_fake_context()
    textile = TinyTextileParser(sys.stdout, fake_context)
    textile.parse(r"""
        a windows path:
        C:\windows\foo\bar
        a linux path:
        /usr/bin/python
        a manuel linebreak\\with two backslashes
    """)

