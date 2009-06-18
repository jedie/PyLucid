# -*- coding: utf-8 -*-

"""
    Generate dynamicly urls based on the database tree
"""

from django.conf.urls.defaults import patterns, url

from pylucid_project.apps.pylucid_update import views
from pylucid.decorators import superuser_only

urlpatterns = patterns('',
    url(r'^$',
        superuser_only(views.menu),
        name='PyLucidUpdate-menu'
    ),
    url(r'^update08/$',
        superuser_only(views.update08),
        name='PyLucidUpdate-update08'
    ),
    url(r'^update08templates/$',
        superuser_only(views.update08templates),
        name='PyLucidUpdate-update08templates'
    ),
    url(r'^update08styles/$',
        superuser_only(views.update08styles),
        name='PyLucidUpdate-update08styles'
    ),
)
