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

__version__ = "$Rev$"


from django.conf import settings
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from django.contrib.comments.views.comments import post_comment

from pylucid_project.apps.pylucid.decorators import render_to

from pylucid_project.pylucid_plugins.blog.models import BlogEntry

# from django-tagging
from tagging.models import Tag, TaggedItem



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
    # Get all blog entries, that the current user can see
    queryset = BlogEntry.objects.all_accessible(request)

    # Limit the queryset with django Paginator
    paginator = BlogEntry.objects.paginate(request, queryset)

    tag_cloud = BlogEntry.objects.get_tag_cloud(request)

    context = {
        "entries": paginator,
        "tag_cloud": tag_cloud,
        "CSS_PLUGIN_CLASS_NAME": settings.PYLUCID.CSS_PLUGIN_CLASS_NAME,
    }
    return context


@render_to("blog/summary.html")
def tag_view(request, tag):
    """
    Display summary list with blog entries filtered by the giben tag.
    """
    tags = tag.strip("/").split("/")

    # Get all blog entries, that the current user can see
    queryset = BlogEntry.objects.all_accessible(request)

    queryset = TaggedItem.objects.get_by_model(queryset, tags)

    # Limit the queryset with django Paginator
    paginator = BlogEntry.objects.paginate(request, queryset)

    # Add link to the breadcrumbs ;)
    _add_breadcrumb(request, title=_("All '%s' tagged items" % ",".join(tags)), url=request.path)

    tag_cloud = BlogEntry.objects.get_tag_cloud(request)

    context = {
        "entries": paginator,
        "tag_cloud": tag_cloud,
        "CSS_PLUGIN_CLASS_NAME": settings.PYLUCID.CSS_PLUGIN_CLASS_NAME,
    }
    return context


@csrf_protect
@render_to("blog/detail_view.html")
def detail_view(request, id, title):
    """
    Display one blog entry with a comment form.
    """
    # Get all blog entries, that the current user can see
    queryset = BlogEntry.objects.all_accessible(request)

    try:
        entry = queryset.get(pk=id)
    except BlogEntry.DoesNotExist:
        msg = "Blog entry doesn't exist."
        if settings.DEBUG or request.user.is_staff:
            msg += " (ID %r wrong.)" % id
        request.page_msg.error(msg)
        return summary(request)

    # Add link to the breadcrumbs ;)
    _add_breadcrumb(request, title=entry.headline, url=entry.get_absolute_url())

    if request.POST:
        # Use django.contrib.comments.views.comments.post_comment to handle a comment
        # post.
        return post_comment(request, next=entry.get_absolute_url())

    tag_cloud = BlogEntry.objects.get_tag_cloud(request)

    context = {
        "page_title": entry.headline, # Change the global title with blog headline
        "entry": entry,
        "tag_cloud": tag_cloud,
        "CSS_PLUGIN_CLASS_NAME": settings.PYLUCID.CSS_PLUGIN_CLASS_NAME,
    }
    return context

