# coding: utf-8

"""
    pylucid.models.Page
    ~~~~~~~~~~~~~~~~~~~

    Old PyLucid v0.8 models, used for migrating data into the new v0.9 models.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: 2009-02-20 09:22:34 +0100 (Fr, 20 Feb 2009) $
    $Rev: 1831 $
    $Author: JensDiemer $

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Group


class PageManager(models.Manager):
    """
    Manager for Page model.
    """
    pass

#______________________________________________________________________________

class Page08(models.Model):
    """
    A CMS Page Object

    TODO: We should refactor the "pre_save" behavior, use signals:
    http://code.djangoproject.com/wiki/Signals
    """

    # IDs used in other parts of PyLucid, too
    MARKUP_CREOLE = 6
    MARKUP_HTML = 0
    MARKUP_HTML_EDITOR = 1
    MARKUP_TINYTEXTILE = 2
    MARKUP_TEXTILE = 3
    MARKUP_MARKDOWN = 4
    MARKUP_REST = 5

    MARKUP_CHOICES = (
        (MARKUP_CREOLE      , u'Creole wiki markup'),
        (MARKUP_HTML        , u'html'),
        (MARKUP_HTML_EDITOR , u'html + JS-Editor'),
        (MARKUP_TINYTEXTILE , u'textile'),
        (MARKUP_TEXTILE     , u'Textile (original)'),
        (MARKUP_MARKDOWN    , u'Markdown'),
        (MARKUP_REST        , u'ReStructuredText'),
    )
    MARKUP_DICT = dict(MARKUP_CHOICES)
    #--------------------------------------------------------------------------

    objects = PageManager()

    # Explicite id field, so we can insert a help_text ;)
    id = models.AutoField(primary_key=True, help_text="The internal page ID.")

    content = models.TextField(blank=True, help_text="The CMS page content.")

    parent = models.ForeignKey(
        "self", null=True, blank=True,
        to_field="id", help_text="the higher-ranking father page",
    )
    position = models.IntegerField(
        default=0,
        help_text="ordering weight for sorting the pages in the menu."
    )

    name = models.CharField(
        blank=False, null=False,
        max_length=150, help_text="A short page name"
    )

    shortcut = models.CharField(
        unique=True, null=False, blank=False,
        max_length=150, help_text="shortcut to built the URLs",

    )
    title = models.CharField(
        blank=True, max_length=150, help_text="A long page title"
    )

    template = models.ForeignKey(
        "Template08", to_field="id", help_text="the used template for this page"
    )
    style = models.ForeignKey(
        "Style08", to_field="id", help_text="the used stylesheet for this page"
    )
    markup = models.IntegerField(
        db_column="markup_id", # Use the old column name.
        max_length=1, choices=MARKUP_CHOICES,
        help_text="the used markup language for this page",
    )

    keywords = models.CharField(
        blank=True, max_length=255,
        help_text="Keywords for the html header. (separated by commas)"
    )
    description = models.CharField(
        blank=True, max_length=255,
        help_text="Short description of the contents. (for the html header)"
    )

    createtime = models.DateTimeField(
        auto_now_add=True, help_text="Create time",
    )
    lastupdatetime = models.DateTimeField(
        auto_now=True, help_text="Time of the last change.",
    )
    createby = models.ForeignKey(
        User, editable=False, related_name="page_createby",
        help_text="User how create the current page.",
    )
    lastupdateby = models.ForeignKey(
        User, editable=False, related_name="page_lastupdateby",
        help_text="User as last edit the current page.",
    )

    showlinks = models.BooleanField(default=True,
        help_text="Put the Link to this page into Menu/Sitemap etc.?"
    )
    permitViewPublic = models.BooleanField(default=True,
        help_text="Can anonymous see this page?"
    )

    permitViewGroup = models.ForeignKey(
        Group, related_name="page_permitViewGroup", null=True, blank=True,
        help_text="Limit viewable to a group?"
    )

    permitEditGroup = models.ForeignKey(
        Group, related_name="page_permitEditGroup", null=True, blank=True,
        help_text="Usergroup how can edit this page."
    )

    class Meta:
        db_table = 'PyLucid_page'
        app_label = 'PyLucid_Update'

    _url_cache = {}
    def get_absolute_url(self):
        """ absolute url *without* language code (without domain/host part) """
        if self.pk in self._url_cache:
            #print "Page08 url cache len: %s, pk: %s" % (len(self._url_cache), self.pk)
            return self._url_cache[self.pk]

        if self.parent:
            parent_shortcut = self.parent.get_absolute_url()
            url = parent_shortcut + self.shortcut + "/"
        else:
            url = "/" + self.shortcut + "/"

        self._url_cache[self.pk] = url
        return url

    def __unicode__(self):
        return u"old page model %r" % self.shortcut



class Template08(models.Model):
    name = models.CharField(unique=True, max_length=150)

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)

    createby = models.ForeignKey(User, related_name="template_createby",
        null=True, blank=True
    )
    lastupdateby = models.ForeignKey(User, related_name="template_lastupdateby",
        null=True, blank=True
    )

    description = models.TextField()
    content = models.TextField()

    def __unicode__(self):
        return u"old page template %r" % self.name

    class Meta:
        db_table = 'PyLucid_template'
        app_label = 'PyLucid_Update'




class Style08(models.Model):
    name = models.CharField(unique=True, max_length=150)

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)

    createby = models.ForeignKey(User, related_name="style_createby",
        null=True, blank=True
    )
    lastupdateby = models.ForeignKey(User, related_name="style_lastupdateby",
        null=True, blank=True
    )

    description = models.TextField(null=True, blank=True)
    content = models.TextField()

    def __unicode__(self):
        return u"old page stylesheet %r" % self.name

    class Meta:
        db_table = 'PyLucid_style'
        app_label = 'PyLucid_Update'


class JS_LoginData08(models.Model):
    """
    SHA information for the PyLucid JS-SHA-Login.
    """
    user = models.ForeignKey(User)

    sha_checksum = models.CharField(max_length=192)
    salt = models.CharField(max_length=5)

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "old JS_LoginData for user '%s'" % self.user.username

    class Meta:
        verbose_name = verbose_name_plural = 'JS-LoginData'
        db_table = 'PyLucid_js_logindata'
        app_label = 'PyLucid_Update'



#______________________________________________________________________________
# Models from old Blog plugin


class BlogComment08(models.Model):
    """
    comment from non-registered users
    """
    blog_entry = models.ForeignKey("BlogEntry", related_name="%(class)s_blog_entry")

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
        _("homepage"), help_text=_("Your homepage (optional)"),
        verify_exists=False, max_length=200,
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
        null=True, blank=True,
        related_name="%(class)s_createby"
    )
    lastupdateby = models.ForeignKey(
        User, editable=False,
        help_text="User as last edit the current comment.",
        null=True, blank=True,
        related_name="%(class)s_lastupdateby"
    )

#    def html_content(self):
#        """
#        returns the content as html used a simple markup.
#        """
#        safe_content = strip_tags(self.content)
#        content = fallback_markup(safe_content)
#        return mark_safe(content)

    class Meta:
        db_table = 'PyLucidPlugins_blogcomment'
        app_label = 'PyLucid_Update'
        ordering = ('createtime', 'lastupdatetime')



BAD_TAG_SLUG_CHARS = (" ", "/", ";")
class BlogTagManager(models.Manager):
    """
    Manager for BlogTag model.
    """
    def safe_get(self, slug):
        """
        Get a tag entry by slug. Try to verify the slug before we access the
        database. Should be used, if the slug comes from the Client
        (e.g. via url)
        TODO: Exist there a better way to verify the tag slug?
        """
        slug = slug.strip("/") # If it comes from url args
        for char in BAD_TAG_SLUG_CHARS:
            if char in slug:
                raise self.model.DoesNotExist("Not allowed character in tag name!")

        return self.model.objects.get(slug=slug)

    def add_new_tags(self, tag_list, blog_obj):
        """
        Create new tag entries and add it to the given blog entry.
        Skip existing tags and returns only the new created tags.
        """
        new_tags = []
        for tag_name in tag_list:
            try:
                tag_obj = self.get(name=tag_name)
            except self.model.DoesNotExist:
                new_tags.append(tag_name)
                tag_obj = self.create(name=tag_name, slug=tag_name)

            # Add many-to-many
            blog_obj.tags.add(tag_obj)

        return new_tags

    def get_tag_info(self):
        """
        Returns all tags with the additional information:
         * tag.count     - How many blog entries used this tag?

        returns min_frequency and max_frequency, too: The min/max usage of all
        tags. Needed to build a tag cloud.
        """
        tags = self.model.objects.all()
        if not tags:
            # There exist no tags
            return [], 0, 0

        frequency = set()
        # get the counter information
        for tag in tags:
            count = tag.blogentry_set.count()
            tag.count = count
            frequency.add(count)

        min_frequency = float(min(frequency))
        max_frequency = float(max(frequency))

        return tags, min_frequency, max_frequency

#    def get_tag_choices(self):
#        """
#        returns >count< tags witch are the most used tags.
#        """
#        tags, min_frequency, max_frequency = self.get_tag_info()
#
#        tags = sorted(tags, key=lambda x: x.count, reverse=True)
#
#        choices = tuple([(t.id, t.name) for t in tags])
#        return choices


class BlogTag(models.Model):
    """
    A blog entry tag
    TODO: Add a usage counter! So we can easy sort from more to less usages and
          building a tag cloud is easier.
    """
    objects = BlogTagManager()

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, max_length=120)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'PyLucidPlugins_blogtag'
        #db_table = 'PyLucidPlugins_blogentry_tags'
        app_label = 'PyLucid_Update'
        ordering = ('name',)


class BlogEntry(models.Model):
    """
    A blog entry
    """
    headline = models.CharField(_('Headline'),
        help_text=_("The blog entry headline"), max_length=255
    )
    content = models.TextField(_('Content'))
    markup = models.IntegerField(
        max_length=1, #choices=Page.MARKUP_CHOICES,
        help_text="the used markup language for this entry",
    )

    tags = models.ManyToManyField(BlogTag, blank=True,
        db_table="PyLucidPlugins_blogentry_tags", related_name="blogentry_tags",
    )

    is_public = models.BooleanField(
        default=True, help_text="Is post public viewable?"
    )

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)
    createby = models.ForeignKey(User,
        editable=False,
        related_name="%(class)s_08_createby"
    )
    lastupdateby = models.ForeignKey(
        User,
        editable=False,
        null=True, blank=True,
        related_name="%(class)s_08_lastupdateby",
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

    class Meta:
        ordering = ('-createtime', '-lastupdatetime')
        db_table = 'PyLucidPlugins_blogentry'
        app_label = 'PyLucid_Update'
