# -*- coding: utf-8 -*-

from PyLucid.system.hightlighter import make_html

def html(args, text):
    """
    Macro tag <<html>>...<</html>>
    Pass-trought for html code (or other stuff) 
    """
    return text

def code(args, text):
    """
    Highlight sourcecode using 
    Macro tag <<code ext=.EXT>>...<</code>>
    """
    if "=" in args:
        source_type = args.split("=")[-1]
    else:
        source_type = ""
        
    return make_html(
        sourcecode = text,
        source_type=source_type,
    )