# coding: utf-8

import os
import posixpath

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"
    virtualenv_file = "../../../../../bin/activate_this.py"
    execfile(virtualenv_file, dict(__file__=virtualenv_file))

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from pygments.lexers._mapping import LEXERS


class HighlightCodeForm(forms.Form):
    sourcecode = forms.CharField(widget=forms.Textarea)
    source_type = forms.ChoiceField(choices=sorted([(aliases[0], name) for _, name, aliases, _, _ in LEXERS.itervalues()]))


class CleanupLogForm(forms.Form):
    LAST_NUMBERS = "n"
    LAST_DAYS = "d"
    LAST_HOURS = "h"

    TYPE_CHOICES = (
        (LAST_NUMBERS, _("keep the last X entries")),
        (LAST_DAYS, _("keep entries from the last X days")),
        (LAST_HOURS, _("keep entries from the last X hours")),
    )
    number = forms.IntegerField(initial=7, min_value=0, help_text=_("Number of entries to be retained."))
    delete_type = forms.ChoiceField(initial=LAST_DAYS, choices=TYPE_CHOICES,
        help_text=_("Witch 'retained' type is the given number?")
    )
    limit_site = forms.BooleanField(initial=True, required=False,
        help_text=_("Limit the query to the current site?")
    )


#-----------------------------------------------------------------------------------------------------------
# overwrite template


class Template(object):
    """ one template file """
    def __init__(self, path, filename, abs_path):
        self.path = path
        self.filename = filename
        self.abs_path = abs_path

    def get_choices(self):
        if "templates" in self.abs_path:
            path = self.abs_path.split("templates", 1)[1]
        else:
            path = self.abs_path
        path = posixpath.normpath(path)
        path = path.lstrip("/")
        return (self.abs_path, path)


class TemplateDir(object):
    """ all template in a settings.TEMPLATE_DIRS """
    def __init__(self, fs_path):
        self.fs_path = fs_path

        self.short_path = self._build_short_path()

        if not os.path.isdir(self.fs_path):
            print "Error: %r doesn't exist!!!" % self.fs_path

        self.templates = []
        self._get_all_files(self.fs_path)

    def _build_short_path(self):
        if self.fs_path.startswith(settings.PYLUCID_BASE_PATH):
            short_path = self.fs_path[len(settings.PYLUCID_BASE_PATH):]
        else:
            short_path = self.fs_path

        short_path = posixpath.normpath(short_path)
        short_path = short_path.strip("/")
        short_path = short_path.rsplit("templates", 1)[0]
        if "/src/" in short_path:
            short_path = short_path.split("/src/")[1]

        return short_path

    def _get_all_files(self, path):
        dir_items = os.listdir(path)
        for dir_item in dir_items:
            if dir_item.startswith("."): # Skip hidden items, e.g.: .svn
                continue

            abs_path = os.path.join(path, dir_item)
            if os.path.isfile(abs_path):
                self.templates.append(Template(path, dir_item, abs_path))
            elif os.path.isdir(abs_path):
                self._get_all_files(abs_path) # go recusive deeper
            else:
                raise AssertionError("item %r not file or dir" % abs_path)


class Templates(object):
    """ all templates """
    def __init__(self, template_dirs):
        self.template_dirs = template_dirs
        self.templates = {}
        for dir in template_dirs:
            self.templates[dir] = TemplateDir(dir)

    def get_choices(self):
        choices = []
        for dir in self.template_dirs:
            templates = self.templates[dir]
            dir_items = []
            for template in templates.templates:
                dir_items.append(template.get_choices())
            dir_items.sort()
            choices.append((templates.short_path, dir_items))

        choices.sort()
        return choices


class ChoiceTemplateField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        super(ChoiceTemplateField, self).__init__(*args, **kwargs)

        templates = Templates(settings.TEMPLATE_DIRS)
        self.choices = [("", "---------")]
        self.choices += templates.get_choices()


class SelectTemplateForm(forms.Form):
    template = ChoiceTemplateField(
        initial="",
        help_text=_("Select the template you would like to overwrite in dbtemplate.")
    )


if __name__ == "__main__":
    from pprint import pprint

    form = SelectTemplateForm()
    pprint(form.fields["template"].choices)

