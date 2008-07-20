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

import datetime

from django.db import models
from django.conf import settings
from django import newforms as forms
from django.utils import feedgenerator
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _

from django.utils import feedgenerator
from django.contrib.syndication.feeds import Feed, FeedDoesNotExist


from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.tools.content_processors import apply_markup
from PyLucid.tools.newforms_utils import StripedCharField
from PyLucid.tools.utils import escape_django_tags
from PyLucid.system.page_msg import PageMessages
from PyLucid.models.Page import MARKUPS

from PyLucid.plugins_internal.blog.blog_cfg import DONT_CHECK, REJECT_SPAM, \
                                                                    MODERATED

# Don't send mails, display them only.
#MAIL_DEBUG = True
MAIL_DEBUG = False

"""
AVAILABLE_FEEDS = {
    ENTRIES_FEED = "all_blog_entries"
    COMMENTS_FEED = "all_blog_comments"
}

FEED_FORMATS = (
    {
        "file_ext": "rss",
        "generator": feedgenerator.Rss201rev2Feed,
    },
    {
        "file_ext": "atom",
        "generator": feedgenerator.Atom1Feed,
    },
)
"""

#______________________________________________________________________________

class BlogComment(models.Model):
    """
    comment from non-registered users
    """
    blog_entry = models.ForeignKey("BlogEntry")

    ip_address = models.IPAddressField(_('ip address'),)
    person_name = models.CharField(
        _("person's name"), max_length=50,
        help_text=_("Your full name (will be published) (required)"),
    )
    email = models.EmailField(
        _('e-mail address'),
        help_text=_("Only for internal use. (will not be published) (required)"),
    )
    homepage = models.URLField(
        _("homepage"), help_text = _("Your homepage (optional)"),
        verify_exists = False, max_length = 200,
        null=True, blank=True
    )

    content = models.TextField(_('content'), max_length=3000)

    is_public = models.BooleanField(_('is public'))

    createtime = models.DateTimeField(
        auto_now_add=True, help_text="Create time",
    )
    lastupdatetime = models.DateTimeField(
        auto_now=True, help_text="Time of the last change.",
    )
    createby = models.ForeignKey(
        User, editable=False,
        help_text="User how create the current comment.",
        null=True, blank=True
    )
    lastupdateby = models.ForeignKey(
        User, editable=False,
        help_text="User as last edit the current comment.",
        null=True, blank=True
    )

    class Admin:
        pass

    class Meta:
        app_label = 'PyLucidPlugins'



class BlogCommentForm(forms.ModelForm):
    """
    Add a new comment.
    """
    person_name = forms.CharField(
        min_length=4, max_length=50,
        help_text=_("Your name."),
    )
    content = StripedCharField(
        label = _('content'), min_length=5, max_length=3000,
        help_text=_("Your comment to this blog entry."),
        widget=forms.Textarea(attrs={'rows': '15'}),
    )

    class Meta:
        model = BlogComment
        # Using a subset of fields on the form
        fields = ('person_name', 'email', "homepage")


class AdminCommentForm(BlogCommentForm):
    """
    Form for editing a existing comment. Only for Admins
    """
    class Meta:
        model = BlogComment
        fields = (
            'ip_address', 'person_name', 'email', "homepage",
            "content", "is_public",
            "createtime", "lastupdatetime", "createby", "lastupdateby"
        )

#______________________________________________________________________________


class BlogTagManager(models.Manager):
    """
    Manager for BlogTag model.
    """
    def get_or_creates(self, tags_string):
        """
        split the given tags_string and create not existing tags.
        returns a list of all tag model objects and a list of all created tags.
        """
        tag_objects = []
        new_tags = []
        for tag_name in tags_string.split(" "):
            tag_name = tag_name.strip().lower()
            try:
                tag_obj = self.get(name = tag_name)
            except self.model.DoesNotExist:
                new_tags.append(tag_name)
                tag_obj = self.create(name = tag_name, slug = tag_name)

            tag_objects.append(tag_obj)

        return tag_objects, new_tags


class BlogTag(models.Model):

    objects = BlogTagManager()

    name = models.CharField(max_length=255, core=True, unique=True)
    slug = models.SlugField(
        unique=True, prepopulate_from=('tag',), max_length=120
    )

    def __unicode__(self):
        return self.name

    class Admin:
        pass

    class Meta:
        app_label = 'PyLucidPlugins'


#______________________________________________________________________________

class BlogEntry(models.Model):
    """
    A blog entry
    """
    headline = models.CharField(_('Headline'),
        help_text=_("The blog entry headline"), max_length=255
    )
    content = models.TextField(_('Content'))
    markup = models.IntegerField(
        max_length=1, choices=MARKUPS,
        help_text="the used markup language for this entry",
    )

    tags = models.ManyToManyField(BlogTag, blank=True)

    is_public = models.BooleanField(
        default=True, help_text="Is post public viewable?"
    )

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)
    createby = models.ForeignKey(User,
        editable = False,
    )
    lastupdateby = models.ForeignKey(
        User,
        editable = False,
        null=True, blank=True
    )

    def html_content(self, context):
        """
        returns the generatet html code from the content applyed the markup.
        """
        return apply_markup(
            content = self.content,
            context = context,
            markup_no = self.markup
        )

    def get_tag_string(self):
        """
        Returns all tags as a joined string
        """
        tags = self.tags.all()
        tags_names = [i.name for i in tags]
        return " ".join(tags_names)

    def __unicode__(self):
        return self.headline

    class Admin:
        pass

    class Meta:
        app_label = 'PyLucidPlugins'
        ordering = ('-createtime', '-lastupdatetime')

'''
class RssBlogEntryFeed(Feed):
    """
    TODO!
    http://www.djangoproject.com/documentation/syndication_feeds/
    """
    title = "Blog entry feed"
    link = "/TODO/"
    description = "FIXME"

    def items(self):
        return BlogEntry.objects.filter(is_public=True).all()[:count]

class AtomBlogEntryFeed(RssBlogEntryFeed):
    feed_type = Atom1Feed
    subtitle = RssBlogEntryFeed.description

class BlogEntryForm(forms.ModelForm):
    """
    Form for create/edit a blog entry.
    """
    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': '15'}),
    )

    tags = forms.CharField(
        max_length=255, required=False,
        help_text=_("Tags for this entry (separated by spaces.)"),
        widget=forms.TextInput(attrs={'class':'bigger'}),
    )
    class Meta:
        model = BlogEntry
'''

#______________________________________________________________________________


PLUGIN_MODELS = (BlogComment, BlogTag, BlogEntry,)





class blog(PyLucidBasePlugin):

    keyword_cache = {}

    def __init__(self, *args, **kwargs):
        super(blog, self).__init__(*args, **kwargs)

        # Log info about handling blog comment submissions
        self.submit_msg = PageMessages(
            self.request, use_django_msg=False, html=False
        )

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
        for entry in entries:
            # add tag_info
            tags = []
            for tag in entry.tags.all():
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

        self._render_template("display_blog", context)#, debug=2)

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

        max = self._get_max_count()
        entries = entries.all()[:max]

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
                msg = "Wrong url."
                if self.request.debug:
                    msg += " Blog entry is not public"
                self.page_msg.red(msg)
                return

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
            "back_url": self.URLs.methodLink("lucidTag"),
        }

        self._list_entries([blog_entry], context, full_comments=True)


    def tag(self, urlargs):
        """
        Display all blog entries with the given tag.
        """
        slug = urlargs.strip("/")
        # TODO: Verify tag
        tag_obj = BlogTag.objects.get(slug = slug)

        self.current_page.title += (
            " - " + _("all blog entries tagged with '%s'")
        ) % tag_obj.name

        entries = tag_obj.blogentry_set

        if self.request.user.is_anonymous():
            entries = entries.filter(is_public = True)

        max = self._get_max_count()
        entries = entries.all()[:max]

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
                if blog_obj == None:
                    # a new blog entry should be created
                    blog_obj = BlogEntry(
                        headline = form.cleaned_data["headline"],
                        content = form.cleaned_data["content"],
                        markup = form.cleaned_data["markup"],
                        is_public = form.cleaned_data["is_public"],
                        createby = self.request.user,
                    )
                    blog_obj.save()
                    self.page_msg.green("New blog entry created.")
                    tags_string = form.cleaned_data["tags"]
                else:
                    # Update a existing blog entry
                    tags_string = form.cleaned_data.pop("tags")
                    self.page_msg.green("Update existing blog entry.")
                    blog_obj.lastupdateby = self.request.user
                    for k,v in form.cleaned_data.iteritems():
                        setattr(blog_obj, k, v)

                tag_objects, new_tags = BlogTag.objects.get_or_creates(
                    tags_string
                )
                if new_tags:
                    self.page_msg(_("New tags created: %s") % new_tags)

                # Add many-to-many
                for tag in tag_objects:
                    blog_obj.tags.add(tag)

                blog_obj.save()

                return self.lucidTag()
        else:
            if blog_obj == None:
                context["legend"] = _("Create a new blog entry")

                form = BlogEntryForm(
                    initial={
                        "markup": self.preferences["default_markup"],
                    }
                )
            else:
                context["legend"] = _("Edit a existing blog entry")
                form = BlogEntryForm(
                    instance=blog_obj,
                    initial={"tags":blog_obj.get_tag_string()}
                )

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
            msg = "Wrong url"
            if self.request.debug:
                msg += " %s" % err
            self.page_msg.red(msg)
            return

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
            self.submit_msg("Blog comment published.")
            mail_title = _("Blog comment published.")
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

#        CommentForm = AdminCommentForm
#
#
#        CommentForm = forms.form_for_instance(
#            instance=comment_entry#, form=BlogCommentForm
#        )

        blog_entry = comment_entry.blog_entry # ForeignKey("BlogEntry")

        if self.request.method == 'POST':
#            form = CommentForm(self.request.POST)
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
#            form = CommentForm()
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
'''
    def get_feeds_info(self):
        # return the existing feed names
        return (ENTRIES_FEED, COMMENTS_FEED)

    def feed(self, feed_name, FeedGenerator, count=10):
        """
        Feeds
        * RSS 2.0 / Atom for all entries
        * RSS 2.0 / Atom for the comments

        FeedGenerator = django.utils.feedgenerator.Atom1Feed
        or
        FeedGenerator = django.utils.feedgenerator.Rss201rev2Feed


        RSSfeedGenerator.lucidTag
            - Generates a list of all available feeds
            - The links are always /feed/PluginName/FeedName/FeedType.xml

        /_command/1/RSSfeedGenerator/


        """
        title = self.preferences["blog_title"]

        if feed_name == ENTRIES_FEED:
            model = BlogEntry
            title += " - all blog entries"

        elif feed_name == COMMENTS_FEED:
            model = BlogComment
            title += " - all blog comments"

        else:
            raise AttributeError("Wrong feed_name.")

        items = model.objects.filter(is_public=True).all()[:10]

        link = self.URLs.methodLink("feed", feed_name)

        feed = self._get_feed(FeedGenerator, items, title, link)

        return feed.writeString('utf8')


    def _get_feed(self, FeedGenerator, items, title, link):
        """
        returns the generated feed.
        """
        feed = FeedGenerator(
            title = title,
            link = self.URLs.make_absolute_url(link),
            description = self.preferences.get("description", ""), # XXX
            language = self.preferences.get("language", u"en"), # XXX
        )
        for item in items:
            feed.add_item(
                title = item.headline,
                link = self.URLs.make_absolute_url(
                    self.URLs.methodLink("detail", item.id)
                ),
                description = item.html_content(self.context),
            )

        return feed
'''

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