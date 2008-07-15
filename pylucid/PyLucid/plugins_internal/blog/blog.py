# -*- coding: utf-8 -*-

"""
    PyLucid blog plugin
    ~~~~~~~~~~~~~~~~~~~

    A simple blog system.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__= "$Rev:$ Alpha"

from django.db import models
from django.conf import settings
from django import newforms as forms
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _

from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.tools.content_processors import apply_markup
from PyLucid.models.Page import MARKUPS


#______________________________________________________________________________


class BlogComment(models.Model):
    """
    comment from non-registered users
    """
    blog_entry = models.ForeignKey("BlogEntry")

    ip_address = models.IPAddressField(_('ip address'),)
    person_name = models.CharField(
        _("person's name"), max_length=50
    )
    email = models.EmailField(
        _('e-mail address'),
        help_text="Only for internal use.",
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
        User, editable=False, #related_name="pref_createby",
        help_text="User how create the current comment.",
        null=True, blank=True
    )
    lastupdateby = models.ForeignKey(
        User, editable=False, #related_name="pref_lastupdateby",
        help_text="User as last edit the current comment.",
        null=True, blank=True
    )

    class Admin:
        pass

    class Meta:
        app_label = 'PyLucidPlugins'


class BlogCommentForm(forms.ModelForm):
    """
    Add a comment.
    """
    person_name = forms.CharField(
        min_length=4, max_length=50,
        help_text=_("Your name."),
    )
    content = forms.CharField(
        label = _('content'), min_length=5, max_length=3000,
        help_text=_("Your comment to this blog entry."),
        widget=forms.Textarea(attrs={'rows': '15'}),
    )

    class Meta:
        model = BlogComment
        # Using a subset of fields on the form
        fields = ('person_name', 'email', "comment")


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
        return self.tag

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


#______________________________________________________________________________


PLUGIN_MODELS = (BlogComment, BlogTag, BlogEntry,)




class blog(PyLucidBasePlugin):

    def _list_entries(self, entries, context={}, full_comments=False):
        """
        Build the list of all blog entries.
        """
        # Change the page title.
        preferences = self.get_preferences()
        self.current_page.title = preferences["blog_title"]

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
                entry.all_comments = entry.blogcomment_set.all()
            else:
                entry.add_comment_url = self.URLs.methodLink(
                    "add_comment", entry.id
                )

                entry.comment_count = entry.blogcomment_set.count()
                if entry.comment_count > 0:
                    entry.comment_url = self.URLs.methodLink(
                        "detail", entry.id
                    )

            if self.request.user.is_staff: # Add admin urls
                entry.edit_url = self.URLs.methodLink("edit", entry.id)
                entry.delete_url = self.URLs.methodLink("delete", entry.id)

        context["entries"] = entries

        if self.request.user.is_staff:
            context["create_url"] = self.URLs.methodLink("add_entry")

        self._render_template("display_blog", context)#, debug=2)

    def lucidTag(self):
        """
        display the blog.
        """
        max = self.get_preferences()["max_count"]

        entries = BlogEntry.objects.filter(is_public = True).all()[:max]
        self._list_entries(entries)

    def detail(self, urlargs):
        blog_entry = self._get_blog_from_url(urlargs)
        if not blog_entry:
            # Wrong url, page_msg was send to the user
            return

        context = {
            "back_url": self.URLs.methodLink("lucidTag")
        }

        self._list_entries([blog_entry], context, full_comments=True)


    def tag(self, urlargs):
        """
        Display all blog entries with the given tag.
        """
        max = self.get_preferences()["max_count"]

        slug = urlargs.strip("/")
        # TODO: Verify tag
        tag_obj = BlogTag.objects.get(slug = slug)
        self.page_msg.green(
            "Display only blog entries taged with '%s'" % tag_obj.name
        )
        entries = tag_obj.blogentry_set.filter(is_public = True).all()[:max]

        context = {
            "back_url": self.URLs.methodLink("lucidTag")
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
                else:
                    # Update a existing blog entry
                    blog_obj.lastupdateby = self.request.user
                    for k,v in form.cleaned_data.iteritems():
                        setattr(blog_obj, k, v)
                    self.page_msg.green("Update existing blog entry.")

                tags_string = form.cleaned_data["tags"]
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
                preferences = self.get_preferences()

                form = BlogEntryForm(
                    initial={
                        "markup": preferences["default_markup"],
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

    def _get_blog_from_url(self, urlargs):
        """
        returns the blog model object based on a ID in the url.
        """
        try:
            entry_id = int(urlargs.strip("/"))
            return BlogEntry.objects.get(id = entry_id)
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
        entry = self._get_blog_from_url(urlargs)
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
        entry = self._get_blog_from_url(urlargs)
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

    def add_comment(self, urlargs):
        blog_entry = self._get_blog_from_url(urlargs)
        if not blog_entry:
            # Wrong url, page_msg was send to the user
            return

        if self.request.method == 'POST':
            form = BlogCommentForm(self.request.POST)
            self.page_msg(self.request.POST)
            if form.is_valid():
                self.page_msg(form.cleaned_data)

                is_public = False # TODO

                new_comment = BlogComment(
                    blog_entry = blog_entry,
                    ip_address = self.request.META.get('REMOTE_ADDR'),
                    person_name = form.cleaned_data["person_name"],
                    email = form.cleaned_data["email"],
                    content = form.cleaned_data["content"],
                    is_public = is_public,
                    createby = self.request.user,
                )
                new_comment.save()
                self.page_msg.green("comment saved.")
                return self.lucidTag()
        else:
            form = BlogCommentForm()

        context = {
            "blog_entry": blog_entry,
            "form": form,
        }

        self._render_template("add_comment", context)#, debug=2)

    def mod_comments(self):
        """
        moderate new comments.
        """
        pass
