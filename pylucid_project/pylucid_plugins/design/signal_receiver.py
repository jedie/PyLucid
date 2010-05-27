# coding: utf-8

"""
    PyLucid design plugin
    ~~~~~~~~~~~~~~~~~~~~~

    signal receiver, connected in design.__init__.py

    switch design, if "design_switch_pk" in request.session

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string


def pre_render_global_template_handler(**kwargs):
    """
    Handle the 'pre_render_global_template' signal.
    """
    request = kwargs["request"]
    if "design_switch_pk" not in request.session:
        # The user has not switch the design
        return

    from pylucid_project.apps.pylucid.models import Design # import here, agains import loops

    pagetree = request.PYLUCID.pagetree

    design_id = request.session["design_switch_pk"]
    pagetree.design = Design.on_site.get(id=design_id)
