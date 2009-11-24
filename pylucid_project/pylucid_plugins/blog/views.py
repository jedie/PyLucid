# coding: utf-8

"""
    PyLucid blog plugin
    ~~~~~~~~~~~~~~~~~~~

    A simple blog system.

    http://feedvalidator.org/
    
    TODO:
        * Detail view, use BlogEntry.get_absolute_url()
    

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__ = "$Rev$ Alpha"

# from python core
import os, datetime, posixpath

# from django
from django import http
from django.conf import settings
from django.core.mail import send_mail
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from django.contrib.comments.views.comments import post_comment

from pylucid.decorators import render_to

from blog.models import BlogEntry

# from django-tagging
from tagging.models import Tag, TaggedItem


def _get_filters(request):
    """
    Construct queryset filter.
    Used for blog entry filtering and for Tag.objects.cloud_for_model()
    """
    current_lang = request.PYLUCID.language_entry
    filters = {"language":current_lang}

    if not request.user.has_perm("blog.change_blogentry"):
        filters["is_public"] = True

    return filters


def _filter_blog_entries(request, queryset):
    filters = _get_filters(request)
    queryset = queryset.filter(**filters)
    return queryset


def _get_tag_cloud(request):
    filters = _get_filters(request)
    tag_cloud = Tag.objects.cloud_for_model(BlogEntry, steps=2, filters=filters)
    return tag_cloud


def _add_breadcrumb(request, title, url):
    """ shortcut for add breadcrumb link """
    context = request.PYLUCID.context
    breadcrumb_context_middlewares = context["context_middlewares"]["breadcrumb"]
    # Blog entries have only a headline, use it for name and title
    breadcrumb_context_middlewares.add_link(title, title, url)


@render_to("blog/summary.html")
def summary(request):
    """
    Display summary list with all blog entries.
    """
    queryset = BlogEntry.on_site
    queryset = _filter_blog_entries(request, queryset)
    context = {
        "entries": queryset,
        "tag_cloud": _get_tag_cloud(request),
        "CSS_PLUGIN_CLASS_NAME": settings.PYLUCID.CSS_PLUGIN_CLASS_NAME,
    }
    return context


@render_to("blog/summary.html")
def tag_view(request, tag):
    """
    Display summary list with blog entries filtered by the giben tag.
    """
    tags = tag.strip("/").split("/")
    queryset = TaggedItem.objects.get_by_model(BlogEntry, tags)
    queryset = _filter_blog_entries(request, queryset)

    # Add link to the breadcrumbs ;)
    _add_breadcrumb(request, title=_("All '%s' tagged items" % ",".join(tags)), url=request.path)

    context = {
        "entries": queryset,
        "tag_cloud": _get_tag_cloud(request),
        "CSS_PLUGIN_CLASS_NAME": settings.PYLUCID.CSS_PLUGIN_CLASS_NAME,
    }
    return context


@csrf_protect
@render_to("blog/detail_view.html")
def detail_view(request, id, title):
    entry = BlogEntry.objects.get(pk=id)

    # Add link to the breadcrumbs ;)
    _add_breadcrumb(request, title=entry.headline, url=entry.get_absolute_url())

    if request.POST:
        # Use django.contrib.comments.views.comments.post_comment to handle a comment
        # post.
        return post_comment(request, next=entry.get_absolute_url())

    context = {
        "page_title": entry.headline, # Change the global title with blog headline
        "entry": entry,
        "tag_cloud": _get_tag_cloud(request),
        "CSS_PLUGIN_CLASS_NAME": settings.PYLUCID.CSS_PLUGIN_CLASS_NAME,
    }
    return context


def lucidTag(request):
    """
    TODO: Update the page automaticly???
    """
    return u"[Update Info: You must delete this PageTree entry and create a new blog plugin page here!]"
