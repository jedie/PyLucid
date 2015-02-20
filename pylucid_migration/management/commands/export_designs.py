# coding: utf-8

"""
    export pylucid v1 designs
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import shutil

from django.core.management.base import BaseCommand
from django.template import TemplateDoesNotExist
from django.template.loaders import app_directories

from pylucid_migration.models import Design, PageTree, DBTemplate
from pylucid_migration.template_changes import migrate_template
from pylucid_migration.utils import clean_string


PATH_EXPORTED=os.path.join(".", "design_exported")


class Loader(app_directories.Loader):
    is_usable = True


class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def _process_template(self, design, base_out_path):
        template_filename = design.template

        try:
            dbtemplate = DBTemplate.objects.get(name=template_filename)
        except DBTemplate.DoesNotExist:
            self.stdout.write("\tINFO: %r is not a dbtemplate" % template_filename)
            try:
                content, origin = Loader().load_template_source(template_filename)
            except TemplateDoesNotExist:
                self.stderr.write("ERROR: Template not found: %r" % template_filename)
                return
        else:
            content = dbtemplate.content

        content = migrate_template(content)

        filepath=os.path.join(base_out_path, template_filename)
        self._write_file(filepath, content)

    def _process_headfiles(self, design, base_out_path):
        for headfile in design.headfiles.all():
            # self.stdout.write("\t\t%r" % headfile)
            if headfile.render:
                # CSS ColorScheme entries in the content
                colorscheme = design.colorscheme
                content = headfile.get_rendered(colorscheme)
            else:
                content = headfile.content

            headfile_path = os.path.join(base_out_path, headfile.filepath)
            self._write_file(headfile_path, content)

    def handle(self, *args, **options):
        for design in Design.objects.all():
            clean_design_name = clean_string(design.name)
            # raise CommandError('Poll "%s" does not exist' % poll_id)
            self.stdout.write("\n*** %r ***" % clean_design_name)
            self.stdout.write("\t%r" % design)

            sites = design.sites.all()
            count_info=[]
            for site in sites:
                pagetree_count = PageTree.objects.filter(design=design, site=site).count()
                count_info.append((site, pagetree_count))
                self.stdout.write("\tSite %r count: %i" % (site.name, pagetree_count))

            count_info.sort(key=lambda x: x[1])
            most_used_site=count_info[0][0]

            clean_site_name = clean_string(most_used_site.name)

            base_out_path = os.path.join(PATH_EXPORTED, clean_site_name, clean_design_name)

            shutil.rmtree(base_out_path, ignore_errors=True) # TODO: remove later!!!

            self._process_headfiles(design, base_out_path)
            self._process_template(design, base_out_path)

    def _write_file(self, filepath, content):
        self._verbose_makedirs(filepath)
        self.stdout.write("\tcreate %r..." % filepath)
        with open(filepath, "w") as f:
            f.write(content)

    def _verbose_makedirs(self, path):
        path=os.path.dirname(path)
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        #     self.stdout.write("\t\tPath %r already exists, ok." % path)
        # else:
        #     self.stdout.write("\t\tPath %r created, ok." % path)


