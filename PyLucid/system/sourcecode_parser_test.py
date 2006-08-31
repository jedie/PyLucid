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


test_code = '''
curr_line = "\t" * self.tab_dep + "if "+ dictname + ".has_key('" + mstr[1] + "'):\n"
'''


#~ redirector = tools.redirector()
p = sourcecode_parser.python_source_parser()
#~ print p.get_CSS()
p.parse(test_code)
#~ print redirector.get()
#~ print_clean(redirector.get())



#~ print
#~ print "="*80
#~ print

#~ redirector = tools.redirector()
#~ p = sourcecode_parser.python_source_parser()
#~ print p.get_CSS()
#~ f = file(__file__,"rU")
#~ p.parse(f.read())
#~ f.close()
#~ print redirector.get()
#~ print_clean(redirector.get())
