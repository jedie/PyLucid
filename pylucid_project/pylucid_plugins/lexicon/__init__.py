# coding: utf-8

"""
    PyLucid lexicon plugin
    ~~~~~~~~~~~~~~~~~~~~~~

    

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: 2009-08-11 15:39:06 +0200 (Di, 11 Aug 2009) $
    $Rev: 2264 $
    $Author: JensDiemer $

    :copyleft: 2008-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

from pylucid.signals import pre_render_global_template

from lexicon.signal_receiver import pre_render_global_template_handler


pre_render_global_template.connect(pre_render_global_template_handler)
