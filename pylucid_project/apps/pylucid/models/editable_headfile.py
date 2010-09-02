# coding: utf-8

"""
    PyLucid models
    ~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import errno
import codecs
import mimetypes

from django.conf import settings
from django.db.models import signals
from django.db import models, IntegrityError
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.translation import ugettext_lazy as _

# http://code.google.com/p/django-tools/
from django_tools.template import render

from pylucid_project.apps.pylucid.models.base_models import UpdateInfoBaseModel, AutoSiteM2M
from pylucid_project.apps.pylucid.shortcuts import failsafe_message
from pylucid_project.utils.css_color_utils import unify_spelling, \
                                        get_new_css_names, replace_css_name
from pylucid_project.apps.pylucid.system import headfile

# other PyLucid models
from colorscheme import ColorScheme, Color
from design import Design


TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"



class EditableHtmlHeadFileManager(models.Manager):
    def iter_headfiles_by_colorscheme(self, colorscheme):
        designs = Design.objects.all().filter(colorscheme=colorscheme)
        for design in designs:
            headfiles = design.headfiles.all()
            for headfile in headfiles:
                yield headfile

    def get_HeadfileLink(self, filename):
        """
        returns a pylucid.system.headfile.Headfile instance
        """
        db_instance = self.get(filename=filename)
        return headfile.HeadfileLink(filename=db_instance.filename)#, content=db_instance.content)


class EditableHtmlHeadFile(AutoSiteM2M, UpdateInfoBaseModel):
    """
    Storage for editable static text files, e.g.: stylesheet / javascript.

    inherited attributes from AutoSiteM2M:
        sites   -> ManyToManyField to Site
        on_site -> sites.managers.CurrentSiteManager instance

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    objects = EditableHtmlHeadFileManager()

    filepath = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=64,
        help_text=_("MIME type for this file. (Leave empty for guess by filename)")
    )
    html_attributes = models.CharField(max_length=256, null=False, blank=True,
        # TODO: Use this!
        help_text=_('Additional html tag attributes (CSS example: media="screen")')
    )
    render = models.BooleanField(default=False,
        help_text=_("Are there CSS ColorScheme entries in the content?")
    )
    description = models.TextField(null=True, blank=True)
    content = models.TextField()

    def get_filename(self):
        """ returns only the filename """
        return os.path.split(self.filepath)[1]

    def get_color_filepath(self, colorscheme=None):
        """ Colorscheme + filepath """
        if self.render and colorscheme:
            assert isinstance(colorscheme, ColorScheme)
            return os.path.join("ColorScheme_%s" % colorscheme.pk, self.filepath)
        else:
            # The Design or this file used no colorscheme
            return self.filepath

    def get_path(self, colorscheme):
        """ Path for filesystem cache path and link url. """
        return os.path.join(
            settings.PYLUCID.PYLUCID_MEDIA_DIR, settings.PYLUCID.CACHE_DIR,
            self.get_color_filepath(colorscheme)
        )

    def get_cachepath(self, colorscheme):
        """
        Filesystem path with filename.
        TODO: Install section should create the directories!
        """
        return os.path.join(settings.MEDIA_ROOT, self.get_path(colorscheme))

    def get_rendered(self, colorscheme):
        color_dict = colorscheme.get_color_dict()

        for name, value in color_dict.iteritems():
            color_dict[name] = "#%s" % value

        rendered_content = render.render_string_template(self.content, color_dict)
        return rendered_content

    def save_cache_file(self, colorscheme):
        """
        Try to cache the head file into filesystem (Only worked, if python process has write rights)
        Try to create the out path, if it's not exist.
        """
        cachepath = self.get_cachepath(colorscheme)

        def _save_cache_file(auto_create_dir=True):
            if colorscheme:
                rendered_content = self.get_rendered(colorscheme)
            else:
                rendered_content = self.content
            try:
                f = codecs.open(cachepath, "w", "utf8")
                f.write(rendered_content)
                f.close()
            except IOError, err:
                if auto_create_dir and err.errno == errno.ENOENT: # No 2: No such file or directory
                    # Try to create the out dir and save the cache file
                    path = os.path.dirname(cachepath)
                    if not os.path.isdir(path):
                        # Try to create cache path and save file
                        os.makedirs(path)
                        failsafe_message("Cache path %s created" % path)
                        _save_cache_file(auto_create_dir=False)
                        return
                raise

        try:
            _save_cache_file()
        except (IOError, OSError), err:
            failsafe_message("Can't cache EditableHtmlHeadFile into %r: %s" % (cachepath, err))
        else:
            if settings.DEBUG:
                msg = "EditableHtmlHeadFile cached successful into: %r" % cachepath
                failsafe_message(msg)

    def iter_colorschemes(self):
        """ TODO: Optimizes this """
        visited_colorschemes = []
        designs = Design.objects.all().filter()
        for design in designs:
            colorscheme = design.colorscheme
            if colorscheme in visited_colorschemes:
                continue
            headfiles = design.headfiles.all().filter(render=True)
            for headfile in headfiles:
                if headfile == self:
                    visited_colorschemes.append(colorscheme)
                    yield colorscheme

    def get_send_head_file(self, colorscheme):
        """
        return link to request this headfile with pylucid.views.send_head_file
        """
        url = reverse('PyLucid-send_head_file', kwargs={"filepath":self.filepath})
        if colorscheme:
            # Design used a colorscheme
            url += "?ColorScheme=%s" % colorscheme.pk
        return url

    def get_absolute_url(self, colorscheme):
        if not self.render:
            colorscheme = None

        cachepath = self.get_cachepath(colorscheme)

        def get_cached_url():
            if os.path.isfile(cachepath):
                # The file exist in media path -> Let the webserver send this file ;)
                return os.path.join(settings.MEDIA_URL, self.get_path(colorscheme))

        cached_url = get_cached_url()
        if cached_url: # Cache file was created in the past
            return cached_url

        # Create cache file
        self.save_cache_file(colorscheme)

        cached_url = get_cached_url()
        if cached_url: # Use created cache file
            return cached_url

        # Can't create cache file -> use pylucid.views.send_head_file for it
        return self.get_send_head_file(colorscheme)

    def get_headfilelink(self, colorscheme):
        """ Get the link url to this head file. """
        url = self.get_absolute_url(colorscheme)
        return headfile.HeadfileLink(url)

    def delete_cachefile(self, colorscheme):
        cachepath = self.get_cachepath(colorscheme)
        if not os.path.isfile(cachepath):
            if settings.DEBUG:
                failsafe_message("No need to delete cache file %s, it doesn't exist, yet." % cachepath)
            return

        try:
            os.remove(cachepath)
        except Exception, err:
            failsafe_message("Can't delete '%(path)s': %(err)s" % {
                "path": cachepath,
                "err": err
            })
        else:
            failsafe_message("Cache file %s deleted." % cachepath)


    def clean_fields(self, exclude):
        message_dict = {}

        if not self.mimetype and self.filepath:
            # Set mimetype by guess type from filepath
            self.mimetype = self.auto_mimetype()

        if "mimetype" not in exclude:
            all_mimetypes = set(mimetypes.types_map.values())
            if self.mimetype not in all_mimetypes:
                failsafe_message(
                    "Warning: Mimetype %(mimetype)r for headfile %(headfile)r unknown!" % {
                        "mimetype": self.mimetype, "headfile": self.filepath
                    }
                )

        if "filepath" not in exclude:
            try:
                # "validate" the filepath with the url re. 
                reverse('PyLucid-send_head_file', kwargs={"filepath": self.filepath})
            except NoReverseMatch, err:
                message_dict["filepath"] = [_(
                    "filepath %(filepath)r contains invalid characters!"
                    " (Original error: %(err)s)" % {
                        "filepath": self.filepath,
                        "err": err,
                    }
                )]

        if "content" not in exclude and self.render:
            for colorscheme in self.iter_colorschemes():
                existing_colors = colorscheme.get_color_names()
                css_names = get_new_css_names(existing_colors, self.content)
                if css_names:
                    if "content" not in message_dict:
                        message_dict["content"] = []
                    message_dict["content"].append(
                        _("Theses CSS color names %(css_names)s are unknown in %(colorscheme)s") % {
                            "colorscheme": colorscheme,
                            "css_names": ", ".join(["'%s'" % css_name for css_name in css_names])
                        }
                    )

        if message_dict:
            raise ValidationError(message_dict)

    def auto_mimetype(self):
        """ returns the mimetype for the current filename """
        fileext = os.path.splitext(self.filepath)[1].lower()
        if fileext == ".css":
            return u"text/css"
        elif fileext == ".js":
            return u"text/javascript"
        else:
            return mimetypes.guess_type(self.filepath)[0] or u"application/octet-stream"

    def rename_color(self, new_name, old_name):
        """
        Rename a color in headfile content.
        called e.g. from Color model
        """
        # Replace color name in headfile content
        old_content = self.content
        new_content = replace_css_name(old_name, new_name, old_content)
        if old_content == new_content:
            if settings.DEBUG:
                failsafe_message(
                    'Color "{{ %s }}" not exist in headfile "%s"' % (old_name, self.filepath)
                )
            return False
        else:
            self.content = new_content
            self.save()
            if settings.DEBUG:
                failsafe_message(
                    "change color name from '%s' to '%s' in %r" % (old_name, new_name, self.filepath)
                )
            return True

    def update_colorscheme(self):
        """
        merge colors from headfiles with the colorscheme.
        """
        if not self.render:
            # No CSS ColorScheme entries in the content -> do nothing
            return

        existing_color_names = Color.on_site.all().values_list("name", flat=True)

        old_content = self.content
        new_content, color_dict = unify_spelling(existing_color_names, old_content)

        if new_content == old_content:
            failsafe_message("No colors to update, ok.")
            return

        updated_colorschemes = []

        for colorscheme in self.iter_colorschemes():
            updated_colorschemes.append(colorscheme)
            for color_name, color_value in color_dict.iteritems():
                c = Color.objects.create(
                    colorscheme=colorscheme,
                    name=color_name,
                    value=color_value
                )

        failsafe_message("create colors: %(color_dict)r in colorscheme: %(schemes)s" % {
            "color_dict": color_dict,
            "schemes": ", ".join(['"%s"' % s.name for s in updated_colorschemes])
        })

        self.content = new_content


    def save(self, *args, **kwargs):
        self.update_colorscheme()
        super(EditableHtmlHeadFile, self).save(*args, **kwargs)
        for colorscheme in self.iter_colorschemes():
            self.delete_cachefile(colorscheme)

    def __unicode__(self):
        try:
            sites = self.sites.values_list('name', flat=True)
        except ValueError:
            # e.g. new instance not saved, yet: 
            # instance needs to have a primary key value before a many-to-many relationship can be used.
            return u"'%s'" % self.filepath
        else:
            return u"'%s' (on sites: %r)" % (self.filepath, sites)

    class Meta:
        app_label = 'pylucid'
        #unique_together = ("filepath", "site")
        # unique_together doesn't work with ManyToMany: http://code.djangoproject.com/ticket/702
        ordering = ("filepath",)


def unique_check_callback(sender, **kwargs):
    """
    manually check a unique together, because django can't do this with 
    Meta.unique_together and a M2M field. It's also unpossible to do this 
    in model validation.
    
    Obsolete if unique_together work with ManyToMany: http://code.djangoproject.com/ticket/702
    
    Note: this was done in model admin class, too.
    """
    headfile = kwargs["instance"]

    headfiles = EditableHtmlHeadFile.objects.filter(filepath=headfile.filepath)
    headfiles = headfiles.exclude(id=headfile.id)

    for headfile in headfiles:
        for site in headfile.sites.all():
            if site not in headfile.sites.all():
                continue

            raise IntegrityError(
                _("EditableHtmlHeadFile with filepath %(filepath)r exist on site %(site)r") % {
                    "filepath": headfile.filepath,
                    "site": site,
                }
            )

signals.post_save.connect(unique_check_callback, sender=EditableHtmlHeadFile)



