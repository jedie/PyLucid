
"""
    PyLucid defaulttags
    ~~~~~~~~~~~~~~~~~~~

    - register the PyLucid tags
    - put the i18n tags into the builtins, so every internal pages/template can
      use i18n without a explicit {% load i18n %}

    start from:
        ./PyLucid/tools/content_processors.py
    with:
        add_to_builtins('PyLucid.defaulttags')

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: 2008-09-12 13:49:04 +0200 (Fr, 12 Sep 2008) $
    $Rev: 1763 $
    $Author: JensDiemer $

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.template import Library
from django.templatetags.i18n import do_translate, do_block_translate

from pylucid_project.apps.pylucid.defaulttags import lucidTag
from pylucid_project.apps.pylucid.defaulttags import extraheadBlock
from pylucid_project.apps.pylucid.defaulttags import sourcecode
from pylucid_project.apps.pylucid.defaulttags import localtime
#from PyLucid.template_addons.lucidTag import lucidTag
#from PyLucid.template_addons.blocktag_pygments import sourcecode
#from PyLucid.template_addons.filters import chmod_symbol, get_oct, \
#                                                                human_duration

register = Library()

register.tag(lucidTag.lucidTag)
register.tag("extrahead", extraheadBlock.do_extrahead)
register.tag("sourcecode", sourcecode.do_sourcecode)

register.filter("to_utc", localtime.to_utc)

#register.tag(extraheadBlock.ExtraheadNode)
#register.tag(sourcecode)
#register.filter(chmod_symbol)
#register.filter(get_oct)
#register.filter(human_duration)

# register only used tags:
#register.tag('get_available_languages', do_get_available_languages)
#register.tag('get_current_language', do_get_current_language)
#register.tag('get_current_language_bidi', do_get_current_language_bidi)
register.tag('trans', do_translate)
register.tag('blocktrans', do_block_translate)

