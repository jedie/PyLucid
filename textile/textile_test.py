#!/usr/bin/python
# -*- coding: UTF-8 -*-

import textile

testTXT = """Hier ein Textile Test

h1. Das ist eine Überschrift

Hier ein wenig Text
und nocht was

und ende
"""

#~ print textile.textile(form['text'].value, head_offset=0, validate=1, sanitize=0)
print textile.textile( testTXT )
