#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Text-Mails verschicken

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

import sys, time, smtplib
from email.MIMEText import MIMEText

def send_text_email(from_address, to_address, subject, text):
    msg = MIMEText(
        _text = text,
        _subtype = "plain",
        _charset = "UTF-8"
    )
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject
    # Datum nach RFC 2822 Internet email standard.
    msg['Date'] = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
    msg['User-Agent'] = "PyLucid (Python v%s)" % sys.version

    s = smtplib.SMTP()
    s.connect()
    s.sendmail(msg['From'], [msg['To']], msg.as_string())
    s.close()
