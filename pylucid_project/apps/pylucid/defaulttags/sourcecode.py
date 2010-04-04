# coding: utf-8

"""
    PyLucid {% sourcecode %} block tag
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: JensDiemer $

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django import template

from pylucid_project.apps.pylucid.markup.hightlighter import make_html


class SourcecodeNode(template.Node):
    def __init__(self, raw_content, source_type):
        self.raw_content = raw_content
        self.source_type = source_type

    def render(self, context):
        """ put head data into pylucid_plugin.head_files.context_middleware """
        source_html = make_html(
            sourcecode=self.raw_content, source_type=self.source_type,
            django_escape=True
        )
        return source_html


def do_sourcecode(parser, token):
    """
    example:
        {% sourcecode ext=".py" %}
        print "This python script is pygmentize"
        {% endsourcecode %}
    
    With ext argument, get_lexer_by_name used.
    Without it, guess_lexer used. 
    """
    args = token.contents
    try:
        source_type = args.rsplit("=", 1)[-1]
    except (ValueError, IndexError):
        source_type = ""

    # assembles the original content
    raw_content = ""
    while parser.tokens:
        token = parser.next_token()
        if token.token_type == template.TOKEN_TEXT:
            raw_content += token.contents
        elif token.token_type == template.TOKEN_VAR:
            raw_content += "{{ %s }}" % token.contents
        elif token.token_type == template.TOKEN_BLOCK:
            if "endsourcecode" in token.contents:
                # put token back on token list so calling code knows why it terminated
                parser.prepend_token(token)
                break

            raw_content += "{%% %s %%}" % token.contents

    parser.delete_first_token()
    return SourcecodeNode(raw_content, source_type)
do_sourcecode.is_safe = True
