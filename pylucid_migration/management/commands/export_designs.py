import re
import os
import unicodedata

from django.core.management.base import BaseCommand, CommandError
from pylucid_migration.models import Design, PageTree, DBTemplate


BASE_PATH=os.path.join(".", "exported")


def clean_string(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s]', ' ', value).strip()
    return re.sub('[_\s]+', '_', value)



class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        for design in Design.objects.all():
            clean_design_name = clean_string(design.name)
            # raise CommandError('Poll "%s" does not exist' % poll_id)
            self.stdout.write("\n\t*** %r" % clean_design_name)
            self.stdout.write("\t\t%r" % design)

            sites = design.sites.all()
            count_info=[]
            for site in sites:
                pagetree_count = PageTree.objects.filter(design=design, site=site).count()
                count_info.append((site, pagetree_count))
                self.stdout.write("\tSite %r count: %i" % (site.name, pagetree_count))

            count_info.sort(key=lambda x: x[1])
            most_used_site=count_info[0][0]

            clean_site_name = clean_string(most_used_site.name)

            base_out_filename = os.path.join(BASE_PATH, clean_site_name, clean_design_name)
            self.stdout.write("\t\t%r" % base_out_filename)

            self._verbose_makedirs(base_out_filename)

            template_filename = design.template

            try:
                dbtemplate = DBTemplate.objects.get(name=template_filename)
            except DBTemplate.DoesNotExist:
                self.stdout.write("\tINFO: %r is not a dbtemplate" % template_filename)
                # TODO: Try to use normal template loading
            else:
                self.stdout.write("\t\t%r" % dbtemplate)

            # TODO: continue here:


            for headfile in design.headfiles.all():
                self.stdout.write("\t\t%r" % headfile)
                headfile_path = os.path.join(base_out_filename, headfile.filepath)

                self.stdout.write("\t\t%r" % headfile_path)

                if headfile.render:
                    # CSS ColorScheme entries in the content
                    colorscheme = design.colorscheme
                    content = headfile.get_rendered(colorscheme)
                else:
                    content = headfile.content


                # self.stdout.write(content)
                # self.stdout.write("-"*60)




    def _verbose_makedirs(self, path):
            try:
                os.makedirs(path)
            except FileExistsError:
                self.stdout.write("Path %r already exists, ok." % path)
            else:
                self.stdout.write("Path %r created, ok." % path)


