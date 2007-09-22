#!/usr/bin/python2.4
# -*- coding: UTF-8 -*-

"""
    a low level fastCGI test
    ~~~~~~~~~~~~~~~~~~~~~~~~

    The fastCGI test dispatcher.
    Note:
        You need the python package "flup".
        http://trac.saddi.com/flup

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from flup.server.fcgi import WSGIServer
from fastCGI_test_app import app

WSGIServer(app).run()