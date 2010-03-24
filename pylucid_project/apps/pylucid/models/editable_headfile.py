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
from django.contrib.sites.models import Site

# http://code.google.com/p/django-tools/
from django_tools.template import render

from pylucid_project.apps.pylucid.models.base_models import UpdateInfoBaseModel, AutoSiteM2M
from pylucid_project.apps.pylucid.shortcuts import failsafe_message
from pylucid_project.apps.pylucid.system import headfile

from pylucid_project.pylucid_plugins import update_journal

# other PyLucid models
from colorscheme import ColorScheme, Color
from design import Design


TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"



class EditableHtmlHeadFileManager(models.Manager):
    def get_HeadfileLink(self, filename):
        """
        returns a pylucid.system.headfile.Headfile instance
        """
        db_instance = self.get(filename=filename)
        return headfile.HeadfileLink(filename=db_instance.filename)#, content=db_instance.content)


class EditableHtmlHeadFile(AutoSiteM2M, UpdateInfoBaseModel):
    """
    Storage for editable static text files, e.g.: stylesheet / javascript.

    TODO:
    * Check if Design sites in Headfile sites:
        This can't be done in save() method or in signals.post_save, because the related
        objects would be saved later -> It must be done in ManyRelatedManager.
        We should check if django ticked #5390 is done: 
            http://code.djangoproject.com/ticket/5390 # Add signals to ManyRelatedManager

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
    mimetype = models.CharField(max_length=64)
    html_attributes = models.CharField(max_length=256, null=False, blank=True,
        # TODO: Use this!
        help_text='Additional html tag attributes (CSS example: media="screen")'
    )
    render = models.BooleanField(default=False,
        help_text="Are there CSS ColorScheme entries in the content?"
    )
    description = models.TextField(null=True, blank=True)
    content = models.TextField()

    def get_filename(self):
        """ returns only the filename """
        return os.path.split(self.filepath)[1]

    def get_color_filepath(self, colorscheme=None):
        """ Colorscheme + filepath """
        if colorscheme:
            assert isinstance(colorscheme, ColorScheme)
            return os.path.join("ColorScheme_%s" % colorscheme.pk, self.filepath)
        else:
            # The Design used no colorscheme
            return self.filepath

    def get_path(self, colorscheme):
        """ Path for filesystem cache path and link url. """
        return os.path.join(
            settings.PYLUCID.PYLUCID_MEDIA_DIR, settings.PYLUCID.CACHE_DIR,
            self.get_color_filepath(colorscheme)
        )

    def get_cachepath(self, colorscheme):
        """
        filesystem path with filename.
        TODO: Install section sould create the directories!
        """
        return os.path.join(settings.MEDIA_ROOT, self.get_path(colorscheme))

    def get_rendered(self, colorscheme):
        color_dict = Color.objects.get_color_dict(colorscheme)
        return render.render_string_template(self.content, color_dict)

    def save_cache_file(self, colorscheme):
        """
        Try to cache the head file into filesystem (Only worked, if python process has write rights)
        Try to create the out path, if it's not exist.
        """
        cachepath = self.get_cachepath(colorscheme)

        def _save_cache_file(auto_create_dir=True):
            rendered_content = self.get_rendered(colorscheme)
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
                failsafe_message("EditableHtmlHeadFile cached successful into: %r" % cachepath)

    def save_all_color_cachefiles(self):
        """
        this headfile was changed: resave all cache files in every existing colors
        TODO: Update Queyset lookup
        """
        designs = Design.objects.all()
        for design in designs:
            headfiles = design.headfiles.all()
            for headfile in headfiles:
                if headfile == self:
                    colorscheme = design.colorscheme
                    self.save_cache_file(colorscheme)

    def get_absolute_url(self, colorscheme):
        cachepath = self.get_cachepath(colorscheme)
        if os.path.isfile(cachepath):
            # The file exist in media path -> Let the webserver send this file ;)
            return os.path.join(settings.MEDIA_URL, self.get_path(colorscheme))
        else:
            # not cached into filesystem -> use pylucid.views.send_head_file for it
            url = reverse('PyLucid-send_head_file', kwargs={"filepath":self.filepath})
            if colorscheme:
                return url + "?ColorScheme=%s" % colorscheme.pk
            else:
                # Design used no colorscheme
                return url

    def get_headfilelink(self, colorscheme):
        """ Get the link url to this head file. """
        url = self.get_absolute_url(colorscheme)
        return headfile.HeadfileLink(url)

    def auto_mimetype(self):
        """ returns the mimetype for the current filename """
        fileext = os.path.splitext(self.filepath)[1].lower()
        if fileext == ".css":
            return u"text/css"
        elif fileext == ".js":
            return u"text/javascript"
        else:
            mimetypes.guess_type(self.filepath)[0] or u"application/octet-stream"

    def save(self, *args, **kwargs):
        """
        TODO: update if model-validation branch merged into django
        """
        try:
            # "validate" the filepath with the url re. 
            reverse('PyLucid-send_head_file', kwargs={"filepath": self.filepath})
        except NoReverseMatch, err:
            raise ValidationError("filepath %r contains invalid characters!" % self.filepath)

        if self.id == None: # new item should be created.
            # manually check a unique togeher, because django can't do this with a M2M field.
            # Obsolete if unique_together work with ManyToMany: http://code.djangoproject.com/ticket/702
            exist = EditableHtmlHeadFile.on_site.filter(filepath=self.filepath).count()
            if exist != 0:
                # We can use attributes from this model instance, because it needs to have a primary key
                # value before a many-to-many relationship can be used.
                site = Site.objects.get_current()
                raise IntegrityError(
                    "EditableHtmlHeadFile with same filepath exist on site %r" % site
                )

        if not self.mimetype:
            # autodetect mimetype
            self.mimetype = self.auto_mimetype()

        # Try to cache the head file into filesystem (Only worked, if python process has write rights)
        self.save_all_color_cachefiles()

        return super(EditableHtmlHeadFile, self).save(*args, **kwargs)

    def __unicode__(self):
        sites = self.sites.values_list('name', flat=True)
        return u"'%s' (on sites: %r)" % (self.filepath, sites)

    class Meta:
        app_label = 'pylucid'
        #unique_together = ("filepath", "site")
        # unique_together doesn't work with ManyToMany: http://code.djangoproject.com/ticket/702
        ordering = ("filepath",)


#______________________________________________________________________________

def cache_headfiles(sender, **kwargs):
    """
    One colorscheme was changes: resave all cache headfiles with new color values.
    """
    colorscheme = kwargs["instance"]

    designs = Design.objects.all().filter(colorscheme=colorscheme)
    for design in designs:
        headfiles = design.headfiles.all()
        for headfile in headfiles:
            headfile.save_cache_file(colorscheme)

signals.post_save.connect(cache_headfiles, sender=ColorScheme)
