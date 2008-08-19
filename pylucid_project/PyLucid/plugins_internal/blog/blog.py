# -*- coding: utf-8 -*-

"""
    PyLucid blog plugin
    ~~~~~~~~~~~~~~~~~~~

    A simple blog system.

    http://feedvalidator.org/

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__= "$Rev:$ Alpha"

# from python core
import os, datetime, posixpath

# from django
from django.conf import settings
from django.http import HttpResponse
from django.core.mail import send_mail
#from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
#from django import forms
#from django.forms import ValidationError
#from django.contrib.syndication.feeds import Feed, FeedDoesNotExist

# from PyLucid
from PyLucid.tools.utils import escape
from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.tools.utils import escape_django_tags
from PyLucid.system.page_msg import PageMessages
#from PyLucid.tools.forms_utils import InternalURLField
from PyLucid.tools.syndication_feed import FeedFormat, FEED_FORMAT_INFO

# from blog plugin
from PyLucid.plugins_internal.blog.forms import BlogCommentForm, \
                                                AdminCommentForm, BlogEntryForm
from PyLucid.plugins_internal.blog.models import BlogComment, BlogTag, BlogEntry
from PyLucid.plugins_internal.blog.blog_cfg import DONT_CHECK, REJECT_SPAM, \
                                                                    MODERATED

#______________________________________________________________________________

PLUGIN_MODELS = (BlogComment, BlogTag, BlogEntry,)

# Don't send mails, display them only.
#MAIL_DEBUG = True
MAIL_DEBUG = False

#______________________________________________________________________________
# FEEDS

# Don't response the RSS/Atom feed, display it only
#FEED_DEBUG = True
FEED_DEBUG = False

ENTRIES_FEED_NAME = u"entries"
COMMENTS_FEED_NAME = u"comments"
TAG_FEED_PREFIX = u"tag-" # The tag slug would be appended!

#______________________________________________________________________________



class blog(PyLucidBasePlugin):

    keyword_cache = {}

    def __init__(self, *args, **kwargs):
        super(blog, self).__init__(*args, **kwargs)

        # Log info about handling blog comment submissions
        self.submit_msg = PageMessages(
            self.request, use_django_msg=False, html=False
        )

        # URLs
        self.index_url = self.current_page.get_absolute_url()
        self.feed_url_prefix = self.URLs.methodLink("feed")

        # Get the default preference entry.
        self.preferences = self.get_preferences()

        # Change the page title.
        self.current_page.title = self.preferences["blog_title"]

    def _add_comment_admin_urls(self, comments):
        for comment in comments:
            comment.edit_url = self.URLs.methodLink(
                "edit_comment", comment.id
            )
            comment.delete_url = self.URLs.methodLink(
                "delete_comment", comment.id
            )

    def _list_entries(self, entries, context={}, full_comments=False):
        """
        Display the blog.
        As a list of entries and as a detail view (see internal page).
        """
        used_tags = set()
        for entry in entries:
            # add tag_info
            tags = []
            for tag in entry.tags.all():
                used_tags.add(tag) # Used in self._get_tag_feeds_info()
                tags.append({
                    "name": tag.name,
                    "url": self.URLs.methodLink("tag", tag.slug),
                })
            entry.tag_info = tags

            # add html code from the content (apply markup)
            entry.html = entry.html_content(self.context)

            if full_comments:
                # Display all comments
                comments = entry.blogcomment_set
                if self.request.user.is_staff:
                    comments = comments.all()
                    self._add_comment_admin_urls(comments)
                else:
                    comments = comments.filter(is_public = True).all()

                entry.all_comments = comments
            else:
                entry.detail_url = self.URLs.methodLink(
                    "detail", entry.id
                )
                entry.comment_count = entry.blogcomment_set.count()

            if self.request.user.is_staff: # Add admin urls
                entry.edit_url = self.URLs.methodLink("edit", entry.id)
                entry.delete_url = self.URLs.methodLink("delete", entry.id)

        context["entries"] = entries

        if self.request.user.is_staff:
            context["create_url"] = self.URLs.methodLink("add_entry")

        # Add all available syndication feeds information
        context["feed_info"] = self._get_feeds_info()
        context["tag_feed_info"] = self._get_tag_feeds_info(used_tags)

        context["tag_cloud"] = self._get_tag_cloud()

        self._render_template("display_blog", context, debug=0)

    def _get_max_count(self):
        """
        The maximal numbers of blog entries, displayed together.
        FIXME: Use django pagination:
        http://www.djangoproject.com/documentation/pagination/
        """
        if self.request.user.is_anonymous():
            return self.preferences["max_anonym_count"]
        else:
            return self.preferences["max_user_count"]

    def lucidTag(self):
        """
        display the blog.
        """
        # FIXME: Never cache this page.
        self.request._use_cache = False

        self.current_page.title += " - " + _("all entries")

        entries = BlogEntry.objects
        if self.request.user.is_anonymous():
            entries = entries.filter(is_public = True)
        elif self.request.user.is_superuser:
            # Check
            if not self.preferences["notify"]:
                self.page_msg(
                    "Warning: There is no notify email address!"
                    " Please change the blog preferences entry."
                )

        limit = self._get_max_count()
        entries = entries.all()[:limit]

        self._list_entries(entries)

    def detail(self, urlargs):
        """
        Display one blog entry with all comments.
        """
        blog_entry = self._get_entry_from_url(urlargs, model=BlogEntry)
        if not blog_entry:
            # Wrong url, page_msg was send to the user
            return

        self.current_page.title += " - " + blog_entry.headline

        if blog_entry.is_public != True:
            # This blog entry is not public. Comments only allowed from logged
            # in users.
            if self.request.user.is_anonymous():
                return self.error(_("Wrong URL."), "Blog entry is not public")

        if self.request.method == 'POST':
            form = BlogCommentForm(self.request.POST)
            #self.page_msg(self.request.POST)
            if form.is_valid():
                ok = self._save_new_comment(
                    blog_entry, clean_data = form.cleaned_data
                )
                if ok:
                    return self._list_entries([blog_entry], full_comments=True)
        else:
            if self.request.user.is_anonymous():
                initial = {}
            else:
                initial = {
                    "person_name": self.request.user.username,
                    "email": self.request.user.email,
                    "homepage": self.URLs["hostname"],
                }

            form = BlogCommentForm(initial=initial)

        context = {
            #"blog_entry": blog_entry,
            "add_comment_form": form,
            "back_url": self.index_url,
        }

        self._list_entries([blog_entry], context, full_comments=True)


    def tag(self, urlargs):
        """
        Display all blog entries with the given tag.
        """
        slug = urlargs.strip("/")
        # TODO: Exist there a better way to verify the tag slug?
        for char in (" ", "/", ";"):
            if char in slug:
                return self.error(
                    _("Wrong URL."), "Not allowed character in tag name!"
                )

        try:
            tag_obj = BlogTag.objects.safe_get(slug)
        except BlogTag.DoesNotExist, err:
            return self.error(
                _("Wrong URL."), "tag '%s' unknown: %s" % (slug, err)
            )

        self.current_page.title += (
            " - " + _("all blog entries tagged with '%s'")
        ) % tag_obj.name

        entries = tag_obj.blogentry_set

        if self.request.user.is_anonymous():
            entries = entries.filter(is_public = True)

        limit = self._get_max_count()
        entries = entries.all()[:limit]

        context = {
            "back_url": self.URLs.methodLink("lucidTag"),
            "current_tag": tag_obj,
        }

        self._list_entries(entries, context)

    def _create_or_edit(self, blog_obj = None):
        """
        Create a new or edit a existing blog entry.
        """
        context = {
            "url_abort": self.URLs.methodLink("lucidTag")
        }

        if self.request.method == 'POST':
            form = BlogEntryForm(self.request.POST)
            #self.page_msg(self.request.POST)
            if form.is_valid():
                new_tags = form.cleaned_data.pop("new_tags") # ListCharField

                if blog_obj == None: # a new blog entry should be created
                    # take the many-to-many tags objects, for later assign
                    tags = form.cleaned_data.pop("tags")

                    form.cleaned_data["createby"] = self.request.user

                    # Create new blog entry
                    blog_obj = BlogEntry(**form.cleaned_data)
                    blog_obj.save()

                    # Add all tags from the many-to-many tags field
                    blog_obj.tags.add(*tags)

                    self.page_msg.green("New blog entry created.")

                else: # Update a existing blog entry
                    self.page_msg.green("Update existing blog entry.")
                    blog_obj.lastupdateby = self.request.user
                    for k,v in form.cleaned_data.iteritems():
                        setattr(blog_obj, k, v)

                if new_tags != []:
                    # There are new tags to create incoming via ListCharField
                    # Create the new tags and add them to the blog entry
                    new_tags = BlogTag.objects.add_new_tags(new_tags, blog_obj)
                    if new_tags:
                        self.page_msg(_("New tags created: %s") % new_tags)

                blog_obj.save()

                return self.lucidTag()
        else:
            if blog_obj == None:
                context["legend"] = _("Create a new blog entry")
                form = BlogEntryForm(
                    initial={"markup": self.preferences["default_markup"],}
                )
            else:
                context["legend"] = _("Edit a existing blog entry")
                form = BlogEntryForm(instance=blog_obj)

        context["form"]= form

        self._render_template("edit_blog_entry", context)#, debug=True)

    def _get_entry_from_url(self, urlargs, model):
        """
        returns the blog model object based on a ID in the url.
        """
        try:
            entry_id = int(urlargs.strip("/"))
            return model.objects.get(id = entry_id)
        except Exception, err:
            return self.error(_("Wrong URL."), err)

    def delete(self, urlargs):
        """
        Edit a existing blog entry.
        """
        entry = self._get_entry_from_url(urlargs, model=BlogEntry)
        if not entry:
            # Wrong url, page_msg was send to the user
            return

        entry.delete()
        self.page_msg.green("Entry '%s' deleted." % entry)
        return self.lucidTag()

    def edit(self, urlargs):
        """
        Edit a existing blog entry.
        """
        entry = self._get_entry_from_url(urlargs, model=BlogEntry)
        if not entry:
            # Wrong url, page_msg was send to the user
            return

        return self._create_or_edit(entry)

    def add_entry(self):
        """
        Create a new blog entry
        """
        return self._create_or_edit()

    #__________________________________________________________________________
    # COMMENTS

    def _send_notify(self, mail_title, blog_entry, comment_entry):
        """
        Send a email noitify for a submited blog comment.
        """
        email_context = {
            "blog_entry": blog_entry,
            "blog_edit_url": self.URLs.make_absolute_url(
                self.URLs.methodLink("edit", blog_entry.id)
            ),
            "comment_entry": comment_entry,
            "submit_msg": self.submit_msg,
        }

        if hasattr(comment_entry, "id"):
            # Add edit link into the mail
            email_context["edit_url"] = self.URLs.make_absolute_url(
                self.URLs.methodLink("edit_comment", comment_entry.id)
            )

        raw_recipient_list = self.preferences["notify"]
        recipient_list = raw_recipient_list.splitlines()
        recipient_list = [i.strip() for i in recipient_list if i]

        # Render the internal page
        emailtext = self._get_rendered_template(
            "notify_mailtext", email_context#, debug=2
        )

        send_mail_kwargs = {
            "from_email": settings.DEFAULT_FROM_EMAIL,
            "subject": "%s %s" % (settings.EMAIL_SUBJECT_PREFIX, mail_title),
#                from_email = sender,
            "recipient_list": recipient_list,
            "fail_silently": False,
        }

        if MAIL_DEBUG == True:
            self.page_msg("blog.MAIL_DEBUG is on: No Email was sended!")
            self.page_msg(send_mail_kwargs)
            self.response.write("<fieldset><legend>The email text:</legend>")
            self.response.write("<pre>")
            self.response.write(emailtext)
            self.response.write("</pre></fieldset>")
            return
        else:
            send_mail(message = emailtext, **send_mail_kwargs)

    def _reject_spam_comment(self, blog_entry, clean_data):
        """
        Reject a submited comment as spam:
        1. Display page_msg
        2. Handle email notify.
        """
        if not self.preferences["spam_notify"]:
            # Don't send spam notify email
            return

        # Add ID Adress for notify mail text
        clean_data["ip_address"] = self.request.META.get('REMOTE_ADDR')
        clean_data["createtime"] = datetime.datetime.now()

        self._send_notify(
            mail_title = _("blog comment as spam detected."),
            blog_entry = blog_entry, comment_entry = clean_data
        )

    def _check_comment_submit(self, blog_entry, content):
        """
        Check the submit of a new blog comment
        """
        if self.request.user.is_staff:
            # Don't check comments from staff users
            self.submit_msg("comment submit by page member.")
            return _("new blog comment from page member published.")

        # Check the http referer, exception would be raised if something wrong
        self._check_referer(blog_entry)

        content_lower = content.lower()

        # check SPAM keywords
        spam_keyword = self._check_wordlist(
            content_lower, pref_key = "spam_keywords"
        )
        if spam_keyword:
            raise RejectSpam(
                "Comment contains SPAM keyword: '%s'" % spam_keyword
            )

        # check mod_keywords
        mod_keyword = self._check_wordlist(
            content_lower, pref_key = "mod_keywords"
        )
        if mod_keyword:
            raise ModerateSubmit(
                "Comment contains mod_keyword: '%s'" % mod_keyword
            )


    def _save_new_comment(self, blog_entry, clean_data):
        """
        Save a valid submited comment form into the database.

        Check if content is spam or if the comment should be moderated.
        returns True if the comment accepted (is not spam).

        Send notify emails.
        """
        content = clean_data["content"]

        try:
            mail_title = self._check_comment_submit(blog_entry, content)
        except RejectSpam, msg:
            self.page_msg.red("Sorry, your comment identify as spam.")
            self.submit_msg(msg)
            # Display page_msg and handle email notify:
            self._reject_spam_comment(blog_entry, clean_data)
            return False
        except ModerateSubmit, msg:
            self.page_msg(_("Your comment must wait for authorization."))
            mail_title = _("Blog comment moderation needed.")
            self.submit_msg(msg)
            is_public = False
        else:
            msg = _("Blog comment published.")
            self.submit_msg(msg)
            mail_title = msg
            is_public = True

        content = escape_django_tags(content)

        new_comment = BlogComment(
            blog_entry = blog_entry,
            ip_address = self.request.META.get('REMOTE_ADDR'),
            person_name = clean_data["person_name"],
            email = clean_data["email"],
            homepage = clean_data["homepage"],
            content = content,
            is_public = is_public,
            createby = self.request.user,
        )
        # We must save the entry got get the id of it for the notify mail
        new_comment.save()

        # Send a notify email
        self._send_notify(
            mail_title, blog_entry, comment_entry=new_comment
        )

        self.page_msg.green("Your comment saved.")
        return True

    def _get_wordlist(self, pref_key):
        """
        Chached access to the keywords from the preferences.
        (mod_keywords, spam_keywords)
        """
        if pref_key not in self.keyword_cache:
            raw_keywords = self.preferences[pref_key]
            keywords = raw_keywords.splitlines()
            keywords = [word.strip().lower() for word in keywords if word]
            self.keyword_cache[pref_key] = tuple(keywords)

        return self.keyword_cache[pref_key]

    def _check_wordlist(self, content, pref_key):
        """
        Simple check, if the content contains one of the keywords.
        If a keyword found, returns it else returns None
        """
        keywords = self._get_wordlist(pref_key)
        for keyword in keywords:
            if keyword in content:
                return keyword

    def _check_referer(self, blog_entry):
        """
        Check if the referer is ok.
        raise RejectSpam() or ModerateSubmit() if referer is wrong.
        """
        check_referer = self.preferences["check_referer"]
        if check_referer == DONT_CHECK:
            # We should not check the referer
            return

        referer = self.request.META["HTTP_REFERER"]
        should_be = self.URLs.make_absolute_url(
            self.URLs.methodLink("detail", blog_entry.id)
        )
        self.submit_msg("http referer: '%s' - '%s'" % (referer, should_be))

        if referer == should_be:
            # Referer is ok
            return

        msg = "Wrong http referer"

        # Something wrong with the referer
        if check_referer == REJECT_SPAM:
            # We should it rejected as spam
            raise RejectSpam(msg)
        elif check_referer == MODERATED:
            # We should moderate the comment
            raise ModerateSubmit(msg)
        else:
            # Should never appear
            raise AttributeError("Wrong check_referer value?!?")

    def _delete_comment(self, comment_entry):
        """
        Delete one comment entry. Display page_msg.
        Used in delete_comment() and edit_comment().
        """
        old_id = comment_entry.id
        comment_entry.delete()
        self.page_msg.green(_("Comment entry %s deleted." % old_id))

    def delete_comment(self, urlargs):
        """
        Delete a comment (only for admins)
        """
        comment_entry = self._get_entry_from_url(urlargs, model=BlogComment)
        if not comment_entry:
            # Wrong url, page_msg was send to the user
            return

        blog_entry = comment_entry.blog_entry # ForeignKey("BlogEntry")

        self._delete_comment(comment_entry)

        return self._list_entries(
            [blog_entry], context={}, full_comments=True
        )


    def edit_comment(self, urlargs):
        """
        Edit a comment (only for admins)
        """
        comment_entry = self._get_entry_from_url(urlargs, model=BlogComment)
        if not comment_entry:
            # Wrong url, page_msg was send to the user
            return

        blog_entry = comment_entry.blog_entry # ForeignKey("BlogEntry")

        if self.request.method == 'POST':
            form = AdminCommentForm(self.request.POST, instance=comment_entry)
            #self.page_msg(self.request.POST)
            if form.is_valid():
                if "delete" in self.request.POST:
                    self._delete_comment(comment_entry)
                else:
                    form.save()
                    self.page_msg.green("Saved.")
                return self._list_entries(
                    [blog_entry], context={}, full_comments=True
                )
        else:
            form = AdminCommentForm(instance=comment_entry)

        context = {
            "blog_entry": blog_entry,
            "url_abort": self.URLs.methodLink("detail", blog_entry.id),
            "form": form,
        }

        self._render_template("edit_comment", context)#, debug=2)

    def mod_comments(self):
        """
        Build a list of all non public comments
        TODO: make this complete...
        """
        self.page_msg.red("TODO")

        comments = BlogComment.objects.filter(is_public=False)
        self._add_comment_admin_urls(comments)

        context = {
            "comments": comments,
        }

        self._render_template("mod_comments", context)#, debug=2)

    def _feed_filenames(self):
        """
        returns a list of all existing feed filenames
        """
        filenames = []
        filenames.extend([ENTRIES_FEED_NAME, COMMENTS_FEED_NAME])

        tags = self._get_tags()
        filenames.extend([TAG_FEED_PREFIX + tag_slug for tag_slug, _ in tags])

        return filenames

    def _get_feeds_info(self):
        """
        returns information about all available syndication feeds.
        """
        feeds = []

        for feed_name in (ENTRIES_FEED_NAME, COMMENTS_FEED_NAME,):
            feeds.append({
                "url": self.URLs.methodLink("select_feed_format", feed_name),
                "title_info": feed_name,
                "filename": feed_name
            })

        #self.page_msg(feeds)
        return feeds

    def _get_tag_feeds_info(self, used_tags):
        """
        returns information about all available syndication feeds.
        """
        feeds = []
        # Add tag feeds
        for tag in used_tags:
            filename = TAG_FEED_PREFIX + tag.slug
            feeds.append({
                "url": self.URLs.methodLink("select_feed_format", filename),
                "title_info": tag.name,
                "filename": filename
            })

        #self.page_msg(feeds)
        return feeds

    def _get_tag_cloud(self):
        """
        Build the tag cloud context.
        """
        tags, min_frequency, max_frequency = BlogTag.objects.get_tag_info()

        diff_frequency = float(max_frequency - min_frequency)

        max_font_size = self.preferences.get("max_cloud_size", 2.0)
        min_font_size = self.preferences.get("min_cloud_size", 0.7)
        normal_font_size = (max_font_size + min_font_size) / 2.0

        # Calculate and add the font size
        for tag in tags:
            count = float(tag.count)
            try:
                font_size = (
                    (
                        (max_font_size-min_font_size) * (count - min_frequency)
                    ) / diff_frequency
                ) + min_font_size
            except ZeroDivisionError:
                font_size = normal_font_size

            tag.font_size = font_size
            tag.url = self.URLs.methodLink("tag", tag.slug)
            #self.page_msg(tag, count, tag.font_size)

        return tags

    def select_feed_format(self, raw_feed_name=None):
        """
        Build a html page with all existing feed formats
        """
        if raw_feed_name == None:
            return self.error(_("Wrong URL."), "No feed filename given in URL.")

        feed_name = raw_feed_name.strip("/")

        # Verify raw_feed_name
        try:
            self._feed_info_by_filename(feed_name)
        except WrongFeedFilename, err:
            return self.error(_("Wrong URL."), " feed name unknown: %s" % err)

        format_info = []
        for feed_info in FEED_FORMAT_INFO:
            filename = "%s.%s" % (feed_name, feed_info["ext"])
            format_info.append({
                "filename": filename,
                "url": self.URLs.methodLink("feed", filename).rstrip("/"),
                "title": feed_info["title"],
                "info_link": feed_info["info_link"],
                "mime_type": feed_info["generator"].mime_type,
            })

        context = {
            "back_url": self.index_url,
            "format_info": format_info,
        }

        self._render_template("select_feed_format", context, debug=0)

    def _feed_info_by_filename(self, feed_name):
        """
        returns the queryset with all blog entries and a title of the feed.
        raised WrongFeedFilename if feed_name is not valid.
        used in self.select_feed_format() and self.feed()
        """
        if feed_name == ENTRIES_FEED_NAME:
            title = _("Feed with all blog entries")
            queryset = BlogEntry.objects

        elif feed_name == COMMENTS_FEED_NAME:
            title = _("Feed with all blog comments")
            queryset = BlogComment.objects

        elif feed_name.startswith(TAG_FEED_PREFIX):
            # Feed with all blog entries tagged with the given tag
            tag_slug = feed_name[len(TAG_FEED_PREFIX):]
            try:
                tag_obj = BlogTag.objects.safe_get(tag_slug)
            except BlogTag.DoesNotExist, err:
                raise WrongFeedFilename(
                    "tag '%s' unknown: %s" % (tag_slug, err)
                )

            title = _("Feed with all blog entries tagged as '%s'") % (
                tag_obj.name
            )
            queryset = tag_obj.blogentry_set
        else:
            raise WrongFeedFilename("feed name '%s' unknown." % feed_name)

        return queryset, title

    def feed(self, raw_feed_name=None):
        """
        Generate and return a syndication feed.

        feed_name e.g.:
            tag_%s.rss
            tag_%s.atom
            entries .rss/.atom
            comments .rss/.atom
        """
        if raw_feed_name == None:
            return self.error(_("Wrong URL."), "No feed filename given in URL.")

        feed_info = FeedFormat()
        try:
            feed_info.parse_filename(raw_feed_name)
        except Exception, err:
            if self.request.debug: raise
            return self.error(_("Wrong URL."), err)

        feed_name = feed_info["feed_name"]
        format_info = feed_info["format_info"]
        FeedGenerator = format_info["generator"]

        try:
            entries, title = self._feed_info_by_filename(feed_name)
        except WrongFeedFilename, err:
            return self.error(_("Wrong URL."), " feed name unknown: %s" % err)

        title = "%s - %s" % (self.preferences["blog_title"], title)

        # Get the items
        limit = self._get_max_count()
        items = entries.filter(is_public=True).all()[:limit]

        feed = self._get_feed(FeedGenerator, items, title, feed_name)
        feed_content = feed.writeString('utf8')
        content_type = "%s; charset=utf-8" % feed.mime_type

        if FEED_DEBUG:
            self.response.write("<h2>Debug:</h2>")
            self.response.write("content type: %s" % content_type)
            self.response.write("<pre>")
            self.response.write(escape(feed_content))
            self.response.write("</pre>")
            return

        # send the feed as a file to the client
        response = HttpResponse(content_type=content_type)
        response.write(feed_content)
        return response


    def _get_feed(self, FeedGenerator, items, title, feed_name):
        """
        returns the generated feed.
        """
        feed = FeedGenerator(
            title = title,
            link = self.URLs.make_absolute_url(self.index_url),
            description = self.preferences.get("description", ""),
            language = self.preferences.get("language", u"en"),
        )
        for item in items:
            if feed_name == COMMENTS_FEED_NAME:
                # Feed with all comments
                feed.add_item(
                    title = _("Comment from '%s' for blog entry '%s'") % (
                        item.person_name, item.blog_entry.headline
                    ),
                    link = self.URLs.make_absolute_url(
                        self.URLs.methodLink("detail", item.blog_entry.id)
                    ),
                    description = item.content,
                    author_name=item.person_name,
                    pubdate = item.createtime,
                )
            else:
                # Feed with blog entries
                feed.add_item(
                    title = item.headline,
                    link = self.URLs.make_absolute_url(
                        self.URLs.methodLink("detail", item.id)
                    ),
                    description = item.html_content(self.context),
                    author_name=item.createby,
                    pubdate = item.createtime,
                )

        return feed


class WrongReferer(Exception):
    """
    A comment submit was made with a wrong http referer information
    """
    pass

class RejectSpam(Exception):
    """
    A submission was identify as SPAM
    """
    pass

class ModerateSubmit(Exception):
    """
    A submitted comment should be moderated
    """
    pass

class WrongFeedFilename(Exception):
    """
    The feed filename from the url is not valid.
    """
    pass