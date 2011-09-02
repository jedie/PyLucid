# coding:utf-8
"""
    PyLucid managment command
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Create a PyLucid page instance.
    

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from optparse import make_option
import codecs
import os
import shutil

from django.contrib import admin
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import random


ENV_PATH_PLACEHOLDER = '"/please/insert/path/to/PyLucid_env/'


class Command(BaseCommand):
    verbosity = True

    help = (
        "Create a PyLucid page instance\n"
        "destination should be the absolute path for the new page instance."
    )
    args = 'destination'

    option_list = BaseCommand.option_list

    def _set_file_rights(self, *files):
        if self.verbosity:
                self.stdout.write("\n")
        for filename in files:
            filepath = os.path.join(self.destination, filename)
            assert os.path.isfile(filepath)
            if self.verbosity:
                self.stdout.write("set chmod 0755 to: %r\n" % filepath)
            os.chmod(filepath, 0755)
        if self.verbosity:
                self.stdout.write("\n")

    def _verbose_copy(self, src, dst):
        if self.verbosity:
            self.stdout.write("\ncopy: %r\nto: %r\n" % (src, dst))
        shutil.copy2(src, dst)

    def _setup_media(self, function, src, dst):
        if self.verbosity:
            self.stdout.write("\nsrc: %r\ndst: %r\n" % (src, dst))
            self.stdout.flush()
        try:
            function(src, dst)
        except Exception, err:
            self.stderr.write(self.style.ERROR("Error: %s\n" % err))
        else:
            if self.verbosity:
                self.stdout.write("OK\n")

    def _copy_scripts(self, filepath, rel_destination):
        source_path = os.path.join(settings.PYLUCID_BASE_PATH, "../scripts", filepath)
        source_path = os.path.normpath(source_path)
        dst = os.path.join(self.destination, rel_destination)
        self._verbose_copy(source_path, dst)

    def _patch_file(self, filename, patch_data):
        self.stdout.write("\npatch file: %r\n" % filename)
        filepath = os.path.join(self.destination, filename)
        f = codecs.open(filepath, "r", encoding="utf-8")
        content = f.read()
        f.close()

        for placeholder, new_value in patch_data:
            if not placeholder in content:
                self.stderr.write(self.style.ERROR(
                    "Can't patch file %r!\n(String %r not found!)\n" % (filepath, placeholder)
                ))
            else:
                content = content.replace(placeholder, new_value)

        f = codecs.open(filepath, "w", encoding="utf-8")
        f.write(content)
        f.close()
        if self.verbosity:
            self.stdout.write("Update env path in %r\n" % filepath)

    def _patch_env_path(self, *files):
        if self.verbosity:
                self.stdout.write("\n")
        for filename in files:
            self._patch_file(filename,
                patch_data=[(ENV_PATH_PLACEHOLDER, '"%s/' % self.virtual_env_path)]
            )
        if self.verbosity:
                self.stdout.write("\n")

    def handle(self, *args, **options):
        self.verbosity = int(options.get('verbosity', 1))

        if len(args) != 1:
            raise CommandError("missing destination path argument!")

        self.destination = os.path.abspath(args[0])
        self.destination = os.path.normpath(self.destination)

        self.stdout.write("\n\n")
        self.stdout.write("_" * 80)
        self.stdout.write("\n")
        self.stderr.write(self.style.SQL_FIELD("Create a PyLucid page instance"))
        self.stdout.write("\n\n")

        self.stdout.write("source..........: %s\n" % settings.PYLUCID_BASE_PATH)
        self.stdout.write("destination.....: %s\n" % self.style.HTTP_INFO(self.destination))

        self.virtual_env_path = os.path.normpath(os.environ["VIRTUAL_ENV"])
        self.stdout.write("env path........: %s\n" % self.virtual_env_path)

        self.stdout.write("\n")

        if os.path.exists(self.destination):
            self.stderr.write(self.style.NOTICE("destination %r exist! Continue (y/n) ?" % self.destination))
            input = raw_input()
            if input.lower() not in ("y", "j"):
                self.stderr.write("Abort.\n")
                return
        else:
            self.stderr.write(self.style.SQL_COLTYPE("Is destination path ok (y/n) ?"))
            input = raw_input()
            if input.lower() not in ("y", "j"):
                self.stderr.write("Abort.\n")
                return

            if self.verbosity:
                self.stdout.write("create %r\n" % self.destination)
            os.makedirs(self.destination)


        self._copy_scripts("manage.py", "manage.py")
        self._copy_scripts("apache_files/default.htaccess", ".htaccess")
        self._copy_scripts("apache_files/index.fcgi", "index.fcgi")
        self._copy_scripts("apache_files/index.wsgi", "index.wsgi")
        self._copy_scripts("apache_files/index.cgi", "index.cgi")
        self._copy_scripts("apache_files/index.html", "index.html")
        self._copy_scripts("local_settings_example.py", "local_settings.py")


        self.stdout.write("\n")
        self.stdout.write(" -" * 39)
        self.stdout.write("\n")


        # Set path to PyLucid_env in file content:
        self._patch_env_path("manage.py", "index.fcgi", "index.wsgi", "index.cgi")

        # Set chmod 0755 to files:
        self._set_file_rights("manage.py", "index.fcgi", "index.wsgi", "index.cgi")

        django_admin_path = os.path.abspath(os.path.dirname(admin.__file__))
        django_media_src = os.path.join(django_admin_path, "media")
        pylucid_media_src = os.path.join(settings.PYLUCID_BASE_PATH, "media", "PyLucid")
        media_dest = os.path.join(self.destination, "media")

        secret_key = ''.join(
            [random.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)]
        )

        patch_data = [
            (
                'MEDIA_ROOT = "/var/www/YourSite/media/"',
                'MEDIA_ROOT = "%s"' % media_dest
            ),
            (
                'SECRET_KEY = "add-a-secret-key"',
                'SECRET_KEY = "%s"' % secret_key
            ),
            (
                '_CACHE_PATH_PREFIX = os.environ.get("USERNAME", "PyLucid")',
                '_CACHE_PATH_PREFIX = "%s"' % os.environ.get("USERNAME", "PyLucid")
            )
        ]

        self._patch_file("local_settings.py", patch_data)

        self.stdout.write("\n")
        self.stdout.write(" -" * 39)
        self.stdout.write("\n")

        self.stdout.write("media destination..: %s\n" % media_dest)

        if os.path.exists(media_dest):
            if self.verbosity:
                self.stdout.write(self.style.SQL_COLTYPE("\ndestination %r exist.\n" % media_dest))
        else:
            os.makedirs(media_dest)
            if self.verbosity:
                self.stdout.write(self.style.SQL_COLTYPE("\ndestination %r created.\n" % media_dest))

        self.stdout.write(
            "\nYou can copy or symlink the needed media files.\n"
            "We prefer to symlink the files, because they can be easy updated via VCS.\n"
            "But this didn't work if Apache doesn't follow symlinks!\n"
        )
        while True:
            input = raw_input(self.style.NOTICE("Copy or symlink media files (c/s) ?"))
            if input.lower() == "c":
                if self.verbosity:
                    self.stdout.write("\ncopy media files...")
                function = shutil.copytree
                break
            elif input.lower() == "s":
                if self.verbosity:
                    self.stdout.write("\nsymlink media files...")
                function = os.symlink
                break

        self._setup_media(function, django_media_src, os.path.join(media_dest, "django"))
        self._setup_media(function, pylucid_media_src, os.path.join(media_dest, "PyLucid"))


        self.stdout.write("\n")
        self.stdout.write(" -" * 39)
        self.stdout.write("\n")


        self.stdout.write("PyLucid page instance created in:\n%s\n" % self.destination)
        self.stdout.write("Please edit the files for your needs ;)\n")

