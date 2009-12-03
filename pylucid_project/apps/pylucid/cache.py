# coding: utf-8

"""
    PyLucid.cache
    ~~~~~~~~~~~~~

    Cleanup cache after PageTree, PageMeta or PageContent changed.
    
    Cleaning the cache is not only necessary so that the client
    sees the updates also. If a page is no longer accessable for
    anonymous, they should no longer be delivered from the cache.
    
    We clean the complete page cache, because we can't known witch
    part of the cache has been really changed. e.g. the update journal
    is somewhere or if the PageTree hierarchy change...
       
    We used the middlewares:
        django.middleware.cache.UpdateCacheMiddleware
        django.middleware.cache.FetchFromCacheMiddleware
    see also: http://docs.djangoproject.com/en/dev/topics/cache/#the-per-site-cache
    
    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.utils.cache import _generate_cache_header_key

from django.conf import settings
from django.core.cache import cache
from django.contrib.sites.models import Site

from django_tools.middlewares import ThreadLocal

from pylucid_project.apps.pylucid.shortcuts import failsafe_message



class FakeRequest(object):
    """ Used to get the cache key from django.utils.cache._generate_cache_header_key """
    def __init__(self, path):
        self.path = path



def clean_complete_pagecache(sender, **kwargs):
    """
    signal post save handler -> clean all page cache entries
    We simply delete all entries from the cache on this site.
    
    We only cleanup the cache one time in one request.
    We store the information "Cache has been deleted" in the request._cache_cleaned bool.
    In e.g. PyLucid "edit all" view, PageTree, PageMeta and PageContent are stored in series.
    """
    from pylucid_project.apps.pylucid.models import PageMeta # import here, against import loops

    model_instance = kwargs["instance"]

    request = ThreadLocal.get_current_request()
    if request is None:
        if settings.DEBUG:
            failsafe_message("Info: Skip page cache cleanup.")
        return

    verbose = settings.DEBUG or request.user.is_superuser

    cache_cleaned = getattr(request, "_cache_cleaned", False)
    if cache_cleaned:
        # Cache has been deleted in this request.
        if verbose:
            request.page_msg.info(
                "%r was saved. But cache was cleaned in the past, ok." % model_instance
            )
        return

    current_site = Site.objects.get_current()

    queryset = PageMeta.objects.select_related() # PageTree is needed, so select related objects.

    # Cleanup only the current site
    queryset = queryset.filter(pagetree__site=current_site)

    # Use the same key prefix as in django.middleware.cache.FetchFromCacheMiddleware
    key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX

    total_count = 0
    cleaned = 0
    for pagemeta in queryset:
        absolute_url = pagemeta.get_absolute_url()

        # Use the same routine as in django.middleware.cache.FetchFromCacheMiddleware
        fake_request = FakeRequest(path=absolute_url)
        cache_key = _generate_cache_header_key(key_prefix, fake_request)

        if verbose: # Count some information only in verbose mode
            total_count += 1
            is_in_cache = cache.get(cache_key, None) is not None
            if is_in_cache:
                cleaned += 1

        cache.delete(cache_key)

    # store the information "Cache has been deleted" for later signals
    #if request is not None:
    request._cache_cleaned = True

    if verbose:
        msg = (
            "%r was saved, clean page cache:"
            " %s cachable items on this site."
            " %s items deleted from cache."
        ) % (model_instance, total_count, cleaned)
        request.page_msg.successful(msg)
