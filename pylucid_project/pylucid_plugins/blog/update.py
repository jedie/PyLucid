# coding: utf-8

"""
    PyLucid plugin update API
"""

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType

# old models
from pylucid_project.apps.pylucid_update.models import BlogTag, BlogComment08
from pylucid_project.apps.pylucid_update.models import BlogEntry as BlogEntry08

# new model
from blog.models import BlogEntry
from pylucid_comments.models import PyLucidComment


def update08(request, out, language):
    out.write("_" * 79)
    out.write("Update blog data from PyLucid v0.8 to v0.9")
    out.write("")

    # XXX: For dev. only!!!
#    BlogEntry.objects.all().delete()
#    PyLucidComment.objects.all().delete()

    content_type = ContentType.objects.get_for_model(BlogEntry)

    old_blog_entries = BlogEntry08.objects.all()
    for old_blog_entry in old_blog_entries:
        out.write(" convert blog entry: %r" % old_blog_entry.headline)

        old_tags = ",".join(old_blog_entry.tags.values_list('name', flat=True))
        out.write("tags: %r" % old_tags)

        new_entry, created = BlogEntry.on_site.get_or_create(
            headline=old_blog_entry.headline,
            defaults={
                "content": old_blog_entry.content,
                "language": language,
                "markup": old_blog_entry.markup,
                "tags": old_tags,
                "is_public": old_blog_entry.is_public,

                "createby": old_blog_entry.createby,
                "lastupdateby": old_blog_entry.lastupdateby,
            }
        )
        # Set old datetime
        new_entry.createtime = old_blog_entry.createtime
        new_entry.lastupdatetime = old_blog_entry.lastupdatetime,

        new_entry.save()
        if created:
            out.write(" * New blog entry: %r created." % new_entry)
        else:
            out.write(" * blog entry: %r exist." % new_entry)

        old_pylucid_comments = BlogComment08.objects.all().filter(blog_entry=old_blog_entry)
        #old_pylucid_comments = old_blog_entry.blogcomment_set.all()
        out.write("pylucid_comments: %r" % old_pylucid_comments)

        for old_comment in old_pylucid_comments:
            try:
                user = User.objects.get(username=old_comment.person_name)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                try:
                    user = User.objects.get(email=old_comment.email)
                except (User.DoesNotExist, User.MultipleObjectsReturned):
                    user = None

            new_comment, created = PyLucidComment.objects.get_or_create(
                content_type=content_type,
                object_pk=new_entry.pk,
                submit_date=old_comment.createtime,

                defaults={
                    "site": Site.objects.get_current(),

                    "user": user,

                    "user_name": old_comment.person_name,
                    "user_email": old_comment.email,
                    "user_url": old_comment.homepage,

                    "comment": old_comment.content,

                    "ip_address": old_comment.ip_address,
                    "is_public": old_comment.is_public,
                }
            )
            if created:
                out.write(" + New blog comment: %r created." % new_comment)
            else:
                out.write(" + blog comment: %r exist." % new_comment)

        out.write(" -"*49)
