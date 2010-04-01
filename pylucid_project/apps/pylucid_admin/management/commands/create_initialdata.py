
"""
    Create serialized fixture data file for PyLucid initial data.
    
    The order of APP_MODEL_DATA is very important!
    The serialized data must be sorted by topology. 
    Otherwise the dump can't insert back into the database.
    
    TODO: add FIXTURE_FILENAME and FIXTURE_PATH to BaseCommand.option_list
"""
import os
import codecs
import pprint
from optparse import make_option

from django.conf import settings
from django.core import serializers
from django.db.models import get_model
from django.db.models.loading import get_apps, get_models
from django.core.management.base import BaseCommand, CommandError

from pylucid_project.apps.pylucid.tree_model import TreeGenerator



# IMPORANT: ordered by topology!
APP_MODEL_DATA = [
     #['auth', ('Permission', 'Group', 'User', 'Message')],
     #['contenttypes', ('ContentType',)],
     #['sessions', ('Session',)],
     ['sites', ('Site',)],
     #['admin', ('LogEntry',)],
     #['comments', ('Comment', 'CommentFlag')],
     ['pylucid', (
          'Language',
          'ColorScheme', 'Color', 'EditableHtmlHeadFile', 'Design',
          'PageTree', 'PageMeta', 'PageContent', 'PluginPage',
           #'LogEntry',
           #'BanEntry',
           #'UserProfile'
     )],
     #['pylucid_admin', ('PyLucidAdminPage',)],
     #['dbpreferences', ('Preference', 'UserSettings')],
     ['dbtemplates', ('Template',)],
     #['reversion', ('Revision', 'Version')],
     #['tagging', ('Tag', 'TaggedItem')],
     #['redirect', ('RedirectModel',)],
     ['lexicon', ('LexiconEntry',)],
     #['blog', ('BlogEntry',)],
     #['update_journal', ('UpdateJournal', 'PageUpdateListObjects')],
     #['pylucid_comments', ('PyLucidComment',)]
]

FIXTURE_FILENAME = "pylucid.json"

FIXTURE_PATH = os.path.join(settings.PYLUCID_BASE_PATH, "apps", "pylucid_admin", "fixtures")



def get_pagetree_objects(model):
    """
    The PageTree entries must be serialized in the right order. Because they
    have references to him self.
    """
    queryset = model._default_manager.all().order_by("position")
    items = queryset.values("id", "parent")
    tree = TreeGenerator(items, skip_no_parent=True)

    objects = []
    for node in tree.iter_flat_list():
        objects.append(model._default_manager.all().get(id=node.id))

    return objects



class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--list_models', action='store_true',
            help='List all installed models.'),
        make_option('--test', action='store_true',
            help='Test existing PyLucid initial data fixtures.'),

        make_option('--indent', default=4, dest='indent', type='int',
            help='Specifies the indent level to use when pretty-printing output'),
        make_option('-e', '--exclude', default=[], dest='exclude', action='append',
            help='Exclude appname or appname.Model (you can use multiple --exclude)'),
    )

    help = 'Output the contents of the database as a fixture of the given format.'
    args = '[appname ...]'

    def handle(self, *app_labels, **options):
        if options["list_models"]:
            print "List all installed models:"
            data = []
            for app in get_apps():
                app_name = app.__name__.split('.')[-2] # assuming -1 is 'models' and -2 is name
                models = tuple([model.__name__ for model in get_models(app)])
                if models:
                    data.append([app_name, models])
            pprint.pprint(data)
            return

        file_path = os.path.join(FIXTURE_PATH, FIXTURE_FILENAME)

        if options["test"]:
            if not os.path.isfile(file_path):
                print "fixture file not exist: %r" % file_path
                return

            from django.utils import simplejson
            f = codecs.open(file_path, "r", encoding="utf-8")
            data = simplejson.load(f)
            f.close()
            print "loaded %s entries from %s" % (len(data), file_path)
            return

        json_serializer = serializers.get_serializer("json")()

        objects = []
        for app_name, model_names in APP_MODEL_DATA:
            print "App: %r" % app_name
            for model_name in model_names:
                print "\tModel: %r" % model_name
                model = get_model(app_name, model_name)

                if model_name == "PageTree":
                    # Get the PageTree objects ordered by topology!
                    data = get_pagetree_objects(model)
                else:
                    data = model._default_manager.all()

                objects.extend(data)

            print " -" * 39

        if not os.path.isdir(FIXTURE_PATH):
            print "Create dir %r" % FIXTURE_PATH
            os.makedirs(FIXTURE_PATH)

        print "Serialize data and save it into %r..." % FIXTURE_FILENAME
        try:
            with codecs.open(file_path, "w", encoding="utf-8") as out:
                json_serializer.serialize(objects, indent=options['indent'], stream=out,
                    ensure_ascii=False # http://docs.djangoproject.com/en/dev/topics/serialization/#notes-for-specific-serialization-formats
                )
        except Exception, e:
            if options['traceback']:
                raise
            raise CommandError("Unable to serialize database: %s" % e)
        else:
            print "Fixtures written in %r" % file_path

