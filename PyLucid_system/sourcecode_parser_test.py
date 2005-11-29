#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Source Code Parser - TEST
"""

import re

import tools
import sourcecode_parser


clean_re1=re.compile(r'\<span class=".*?"\>')
clean_re2=re.compile(r'\</span\>')

def print_clean(txt):
    txt = txt.encode("String_Escape")
    txt = txt.replace("&nbsp;"," ")
    txt = txt.replace("<br />","\n")
    txt = clean_re1.sub(r"", txt)
    txt = clean_re2.sub(r"", txt)
    print txt


test_code = '''    def find_block(self, textline):
        """This is used to replace following regular expression:
        re.compile(r"<!--\s*BEGIN\s+([a-zA-Z0-9_\-]+)\s+-->")
        re.compile(r"<!--\s*END\s+([a-zA-Z0-9_\-]+)\s+-->")
        """
        block = textline[textline.find('<!--')+4:].lstrip()
        blocktail = block.find('-->')
        if blocktail == -1:
            return [0]
        if block[:5] == 'BEGIN':
            return [1,block[5:blocktail].lstrip().rstrip()]
        elif block[:3] == 'END':
            return [2]
        else:
            return [0]

    def compile_var_tags(self, text_line, lineno):
        "Find and replace tags and blocks variables"
        curr_line = text_line

        mstr = self.find_block(curr_line)
        if mstr[0]:
            if mstr[0] == 1:
                #--------------------------------
                # match <!-- BEGIN var --> block
                curr_line = ''
                if self.cur_scope[-1] == '':
                    dictname = "tpldata"
                else:
                    dictname = "item_" + self.cur_scope[-1]

                curr_line = "\t" * self.tab_dep + "if "+ dictname + ".has_key('" + mstr[1] + "'):\n"
                curr_line = curr_line + "\t" * self.tab_dep + "\tfor item_" + mstr[1] + " in " + dictname + "['" + mstr[1] +"']:"
                self.tab_dep = self.tab_dep + 2
                self.cur_scope.append(mstr[1])

                return curr_line
            elif mstr[0] == 2:
                #-----------------------------
                # match <!-- END var --> block
                self.tab_dep = self.tab_dep - 2
                self.cur_scope.pop()
                if not len(self.cur_scope):
                    self.error_found = 1
                    return '\tappend("Spytee ERROR: END has No matching BEGIN at line ' + str(lineno) + '")'
                return ""
'''


#~ redirector = tools.redirector()
#~ p = sourcecode_parser.python_source_parser()
#~ print p.get_CSS()
#~ p.parse(test_code)
#~ print_clean(redirector.get())



#~ print
#~ print "="*80
#~ print

redirector = tools.redirector()
p = sourcecode_parser.python_source_parser()
print p.get_CSS()
f = file("W:\PyLucid_tarball\_test\spytee\spytee2.py","rU")
p.parse(f.read())
f.close()
#~ print redirector.get()
print_clean(redirector.get())
