# coding: utf-8

"""
    PyLucid lexicon plugin
    ~~~~~~~~~~~~~~~~~~~~~~

    connect signals

    :copyleft: 2009-2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from pylucid_project.apps.pylucid.signals_handlers import pre_render_global_template

from .signal_receiver import pre_render_global_template_handler


pre_render_global_template.connect(pre_render_global_template_handler)
