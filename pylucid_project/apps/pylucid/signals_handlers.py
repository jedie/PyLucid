# coding: utf-8


"""
    PyLucid signals
    ~~~~~~~~~~~~~~~

    :copyleft: 2009-2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.utils.log import getLogger
from django.dispatch.dispatcher import Signal


# see: http://www.pylucid.org/permalink/443/how-to-display-debug-information
log = getLogger("pylucid.signals")


pre_render_global_template = Signal(providing_args=["request", "page_template"])
# post_render_global_template = django.dispatch.Signal(providing_args=["toppings", "size"])


def update_plugin_urls(sender, **kwargs):
    """
    Would be connected in:
        * pylucid.models.pagetree
        * pylucid.models.pluginpage
    """
    # import and connect signal here agains import loops
    from pylucid_project.system.pylucid_plugins import clear_plugin_url_caches
    clear_plugin_url_caches(sender, **kwargs)
