#!/usr/bin/env python
#
# http://www.djangosnippets.org/snippets/1457/
# based on http://www.djangosnippets.org/snippets/662/
# 
# Author:  <greencm@gmail.com>
#
# Purpose: Given a set of classes, sort them such that ones that have
#          ForeignKey relationships with later keys are show up after
#          the classes they depend on
#
# Created: 12/27/07
#
# Modified: 3/20/08
#
# Graham King added the abilility to walk other ManyToMany
# relationships as well as handling fixtures such as content types
#
# Modified: 4/21/09
# Dave Brondsema made it work as a Django management command
# and added ability to exclude apps or models.

import sys
from optparse import OptionParser, make_option

from django.db import models
from django.db.models import get_app, get_apps, get_models
from django.core.management.base import BaseCommand, CommandError
from django.core import serializers


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (make_option('--format', default='json', dest='format',
                               help='Specifies the output serialization format for fixtures.'),
                   make_option('--indent', default=None, dest='indent', type='int',
                               help='Specifies the indent level to use when pretty-printing output'),
                   make_option('-e', '--exclude', default=[], dest='exclude', action='append',
                               help='Exclude appname or appname.Model (you can use multiple --exclude)'),
                   )

    help = 'Output the contents of the database as a fixture of the given format.'
    args = '[appname ...]'

    def handle(self, *app_labels, **options):
        excluded_apps = [get_app(app_label) for app_label in options['exclude'] if "." not in app_label]
        excluded_models = [model.split('.') for model in options['exclude'] if "." in model]

        if len(app_labels) == 0:
            app_list = [app for app in get_apps() if app not in excluded_apps]
        else:
            app_list = [get_app(app_label) for app_label in app_labels]

        # Check that the serialization format exists; this is a shortcut to
        # avoid collating all the objects and _then_ failing.
        if options['format'] not in serializers.get_public_serializer_formats():
            raise CommandError("Unknown serialization format: %s" % options['format'])

        try:
            serializers.get_serializer(options['format'])
        except KeyError:
            raise CommandError("Unknown serialization format: %s" % options['format'])

        objects = []
        models = []
        for app in app_list:
            app_name = app.__name__.split('.')[-2] # assuming -1 is 'models' and -2 is name
            models.extend([model for model in get_models(app) if [app_name, model.__name__] not in excluded_models])
#        models = foreign_key_sort(models)

        for model in models:
            objects.extend(model._default_manager.all())
            print model.__name__

#            try:
#                print serializers.serialize(options['format'], objects, indent=options['indent'])
#            except Exception, e:
#                if options['traceback']:
#                    raise
#                raise CommandError("Unable to serialize database: %s" % e)
