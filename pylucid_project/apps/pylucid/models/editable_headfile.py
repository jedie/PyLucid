# coding: utf-8

"""
    PyLucid models
    ~~~~~~~~~~~~~~

    :copyleft: 2009-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import errno
import codecs
import mimetypes

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.utils.translation import ugettext_lazy as _

# http://code.google.com/p/django-tools/
from django_tools.models import UpdateInfoBaseModel
from django_tools.template import render
from django_tools.utils.messages import failsafe_message

from pylucid_project.utils.css_color_utils import unify_spelling, \
                        get_new_css_names, replace_css_name, unique_color_name
from pylucid_project.apps.pylucid.system import headfile

# other PyLucid models
from colorscheme import ColorScheme, Color
from design import Design


TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"


HEADFILE_CACHE_PATH = os.path.join(
    settings.MEDIA_ROOT, settings.PYLUCID.CACHE_DIR
)
HEADFILE_CACHE_URL = os.path.join(
    settings.MEDIA_URL, settings.PYLUCID.CACHE_DIR
)



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

    def clean_headfile_cache(self):
        """ delete all cache files in cache directory """
        removed_items = []
        def delete_tree(path):
            if not os.path.isdir(path):
                return

            for dir_item in os.listdir(path):
                fullpath = os.path.join(path, dir_item)
                if os.path.isfile(fullpath):
                    removed_items.append(fullpath)
                    os.remove(fullpath)
                elif os.path.isdir(fullpath):
                    delete_tree(fullpath)
                    removed_items.append(fullpath)
                    os.rmdir(fullpath)

        delete_tree(HEADFILE_CACHE_PATH)

        return removed_items


class EditableHtmlHeadFile(UpdateInfoBaseModel):
    """
    Storage for editable static text files, e.g.: stylesheet / javascript.

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    objects = EditableHtmlHeadFileManager()

    filepath = models.CharField(max_length=255, unique=True)
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

    def get_cachepath(self, colorscheme):
        """
        Filesystem path with filename.
        TODO: Install section should create the directories!
        """
        return os.path.join(HEADFILE_CACHE_PATH, self.get_color_filepath(colorscheme))

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
                        msg = "Cache path %s created" % path
#                        print msg
                        failsafe_message(msg)
                        _save_cache_file(auto_create_dir=False)
                        return
                raise

        try:
            _save_cache_file()
        except (IOError, OSError), err:
            msg = "Can't cache EditableHtmlHeadFile into %r: %s" % (cachepath, err)
            msg += ''' You should set settings.PYLUCID.CACHE_DIR="", if cachen can't be used!'''
#            print msg
            failsafe_message(msg)
        else:
            if settings.DEBUG:
                msg = "EditableHtmlHeadFile cached successful into: %r" % cachepath
#                print msg
                failsafe_message(msg)

    def iter_colorschemes(self, skip_colorschemes=None):
        """ TODO: Optimizes this """
        if skip_colorschemes is None:
            skip_colorschemes = []

        designs = Design.objects.all().filter()
        for design in designs:
            colorscheme = design.colorscheme
            if colorscheme in skip_colorschemes:
                continue
            headfiles = design.headfiles.filter(pk=self.pk)
            for headfile in headfiles:
                if headfile == self:
                    skip_colorschemes.append(colorscheme)
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

    def get_absolute_url(self, colorscheme=None):
        """
        return the absolute url to the headfile.      
        Try to cache the headfile into filesystem, if settings.PYLUCID.CACHE_DIR is not empty
        Fallback to send view url, if we can't cache.
        """
        if self.render == True and colorscheme is None:
            raise AssertionError(
                "Headfile %s should renderes, but no colorscheme pass to get_absolute_url()!" % self
            )
        elif self.render == False and colorscheme is not None:
            raise AssertionError(
                "Headfile %s should not rendered, but the colorscheme %s was passed to get_absolute_url()!" % (self, colorscheme)
            )

        if settings.PYLUCID.CACHE_DIR != "":
            cachepath = self.get_cachepath(colorscheme)

            def get_cached_url():
                if os.path.isfile(cachepath):
                    # The file exist in media path -> Let the webserver send this file ;)
                    return os.path.join(HEADFILE_CACHE_URL, self.get_color_filepath(colorscheme))

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
        if self.render != True:
            colorscheme = None

        url = self.get_absolute_url(colorscheme)
        return headfile.HeadfileLink(url)

    def delete_cachefile(self, colorscheme=None):
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

    def delete_all_cachefiles(self):
        if self.render:
            for colorscheme in self.iter_colorschemes():
                self.delete_cachefile(colorscheme)
        else:
            self.delete_cachefile()

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

        if "render" not in exclude and self.render:
            has_colorscheme = False
            designs = Design.objects.all().exclude(colorscheme=None)
            for design in designs:
                its_me = design.headfiles.filter(pk=self.pk).count()
                if its_me:
                    has_colorscheme = True
                    break
            if not has_colorscheme:
                message_dict["render"] = [_("This headfile can't be rendered, because it's not used in a design witch has a colorscheme!")]

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

        # Get all existing color values from content 
        content, content_colors = unify_spelling(self.content)

        # Find the most appropriate entry that has the most match colors.
        best_score = None
        best_colorscheme = None
        tested_colorschemes = 0
        for colorscheme in self.iter_colorschemes():
            tested_colorschemes += 1
            score = colorscheme.score_match(content_colors)
            if score > best_score:
                best_colorscheme = colorscheme
                best_score = score

        if best_colorscheme is None:
            failsafe_message(
                _('No existing colorscheme to merge colors found, ok. (tested %s colorschemes)') % tested_colorschemes
            )
            best_colorscheme_dict = {}
            values2colors = {}
            colorschemes_data = {}
        else:
            failsafe_message(
                _('Merge colors with colorscheme "%(name)s" (score: %(score)s, tested %(count)s colorschemes)') % {
                    "name": best_colorscheme.name,
                    "score": best_score,
                    "count": tested_colorschemes,
                }
            )
            best_colorscheme_dict = best_colorscheme.get_color_dict()
            values2colors = dict([(v, k) for k, v in best_colorscheme_dict.iteritems()])
            colorschemes_data = {best_colorscheme:best_colorscheme_dict}

        existing_color_names = set(best_colorscheme_dict.keys())
        if settings.DEBUG:
            failsafe_message("Use existing colors: %r" % existing_color_names)

        # Check witch colors are not exist in best colorscheme, yet:
        best_colorscheme_values = best_colorscheme_dict.values()
        new_color_values = []
        for color_value in content_colors:
            if color_value not in best_colorscheme_values:
                new_color_values.append(color_value)

        # Collect color information from all other colorschemes witch used this headfile:
        for colorscheme in self.iter_colorschemes(skip_colorschemes=colorschemes_data.keys()):
            color_dict = colorscheme.get_color_dict()
            colorschemes_data[colorscheme] = color_dict
            for color_name, color_value in color_dict.iteritems():
                existing_color_names.add(color_name)
                if color_value not in values2colors:
                    values2colors[color_value] = color_name

        # Create all new colors in any other colorscheme witch used this headfile:
        for new_color_value in new_color_values:
            if new_color_value in values2colors:
                # Use color name from a other colorscheme
                color_name = values2colors[new_color_value]
            else:
                # this color value doesn't exist in any colorscheme, give it a unique name
                color_name = unique_color_name(existing_color_names, new_color_value)
                values2colors[new_color_value] = color_name
                existing_color_names.add(color_name)

        # Replace colors in content and create not existing in every colorscheme
        update_info = {}
        for color_value, color_name in values2colors.iteritems():
            # Replace colors with django template placeholders
            content = content.replace("#%s;" % color_value, "{{ %s }};" % color_name)

            # Create new colors
            for colorscheme in self.iter_colorschemes():
                color_dict = colorschemes_data[colorscheme]
                if color_name in color_dict:
                    # This color exist in this colorscheme
                    continue

                color, created = Color.objects.get_or_create(
                    colorscheme=colorscheme, name=color_name,
                    defaults={"value": color_value}
                )
                color.save()
                if created:
                    if colorscheme not in update_info:
                        update_info[colorscheme] = []
                    update_info[colorscheme].append(color)

        # Create page messages
        for colorscheme, created_colors in update_info.iteritems():
            msg = _('Colors %(colors)s created in colorscheme "%(scheme)s"') % {
                "colors": ", ".join(['"%s:%s"' % (c.name, c.value) for c in created_colors]),
                "scheme": colorscheme.name,
            }
            failsafe_message(msg)

        self.content = content

    def save(self, *args, **kwargs):
        self.update_colorscheme()
        super(EditableHtmlHeadFile, self).save(*args, **kwargs)
        self.delete_all_cachefiles()

    def __unicode__(self):
        return self.filepath

    class Meta:
        app_label = 'pylucid'
        ordering = ("filepath",)




