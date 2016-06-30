
"""
    Small helper command to convert the MySQL engine for all tables.

    See also:

    https://docs.djangoproject.com/en/dev/ref/databases/#storage-engines

    e.g.:

    ./manage.py convert_mysql_engine --database=legacy --engine=InnoDB
"""

from django.db import DEFAULT_DB_ALIAS
from django.core.management.base import BaseCommand
from django.db import connections


class Command(BaseCommand):
    help = "Convert MySQL Engine"

    def add_arguments(self, parser):
        parser.add_argument("--engine", default="InnoDB",
            help="The destination engine, e.g.: InnoDB, MyISAM"
        )
        parser.add_argument('--database', default=DEFAULT_DB_ALIAS,
            help='database to convert. Defaults to the "%s" database.' % DEFAULT_DB_ALIAS
        )

    def handle(self, *args, **options):
        engine = options["engine"].strip()
        print("\nConvert all tables to: %r\n" % engine)

        db = options.get('database')
        connection = connections[db]

        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLE STATUS;")
            for row in cursor.fetchall():
                table_name, used_engine = row[:2]
                self.stdout.write("Convert %r..." % table_name, ending="")

                if used_engine.lower() == engine.lower():
                    self.stdout.write("Skip, is already %r, ok." % engine)
                    continue

                try:
                    # Strange: the table name can't be quoted!
                    cursor.execute("ALTER TABLE %s ENGINE=%%s;" % table_name, [engine])
                except Exception as err:
                    self.stderr.write("Error: %s" % err)
                else:
                    self.stdout.write("OK")
                self.stdout.flush()

        self.stdout.write("\nAll tables converted.")