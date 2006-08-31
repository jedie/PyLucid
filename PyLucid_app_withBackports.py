#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Only for lokal test, PyLucid with backports!
"""

from PyLucid.python_backports import backports

if __name__ == '__main__':
    from colubrid.debug import DebuggedApplication
    from colubrid import execute

    app = DebuggedApplication('PyLucid_app:app')
    execute(app, reload=True, port=8081)
