# -*- coding: utf-8 -*-

"""
    Pygments blocktag
    ~~~~~~~~~~~~~~~~~
    
    Pygments syntax highlighter as a django blocktag
    
    usage:
        {% sourcecode css %}
        .xs {font-family:verdana,arial,helvetica,sans-serif;font-size: x-small}
        .m {font-size: medium}
        
        .line { with:10px }
        {% endsourcecode %}

    registered in: ./PyLucid/defaulttags/__init__.py

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.template import Node, TemplateSyntaxError

from PyLucid.system.hightlighter import make_html

class SourcecodeNode(Node):
    def __init__(self, nodelist, ext):
        self.nodelist = nodelist
        self.ext = ext

    def render(self, context):
        return make_html(
            sourcecode = self.nodelist.render(context),
            source_type=self.ext
        )

def sourcecode(parser, token):
    nodelist = parser.parse(('endsourcecode',))
    parser.delete_first_token()
    varlist = token.contents.split()
    if len(varlist)!=2:
        raise TemplateSyntaxError(
            'Wrong sourcecode blocktag syntax!'
            ' Example: {% sourcecode py %}print "HelloWorld"{% endsourcecode %}'
        )
    ext = varlist[1]
    return SourcecodeNode(nodelist, ext)
