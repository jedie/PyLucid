# -*- coding: utf-8 -*-

#_____________________________________________________________________________
# meta information
__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "Includes Websites into your page."
__long_description__ = """
Includes a remote website into your CMS page.

=== parameters


==== url:

The url to get.


==== title:

A title for the fieldset header.


==== preformat:

Is the content preformatted text? Should we surround it with <pre> tags?

preformat="None":
    Automatic modus. If content type is html, don't surround with <pre> tag,
    else add <pre> tag.

preformat="True":
    always add <pre> tag.

preformat="False":
    don't add <pre> tag


==== escape:

Is the receaved content safe (escape=False) or should we escape all html
entries (escape=True)?
"""

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
    "lucidTag" : {
        "must_login"    : False,
        "must_admin"    : False,
    }
}
