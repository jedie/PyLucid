# -*- coding: utf-8 -*-

"""
    Generate dynamicly urls based on the database tree
"""

from django.conf.urls.defaults import url

from pylucid_project.apps.pylucid.models import Page08

PAGE_VIEW = 'pylucid_project.apps.pylucid.views.get_page'

def dynamic_cms_urls():
    result = []
    pages = Page08.objects.all()
    for page in pages:
        page_url = page.get_absolute_url()
        page_url = page_url.lstrip("/")
        page_re = '^%s$' % page_url
        
        slug = page.shortcut 

        result.append(
            url(page_re, PAGE_VIEW, kwargs={"page_id": page.id}, name='page-%s' % slug)
        )
    return tuple(result)