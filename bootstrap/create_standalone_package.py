#!/usr/bin/env python
# coding: utf-8

"""
    Create from a existing Pylucid virtual environment a standalone package.
"""

import os
import sys
import shutil
import optparse
import warnings
import subprocess
import pkg_resources
import time
import codecs
import random


__version__ = (0, 2, 1)


#------------------------------------------------------------------------------


VERSION_STRING = '.'.join(str(part) for part in __version__)


#GET_GIT_VER_VERBOSE = True
GET_GIT_VER_VERBOSE = False

def _error(msg):
    if GET_GIT_VER_VERBOSE:
        warnings.warn(msg)
    return ""

def get_commit_timestamp(path=None):
    if path is None:
        path = os.path.abspath(os.path.dirname(__file__))

    try:
        process = subprocess.Popen(
            # %ct: committer date, UNIX timestamp  
            ["/usr/bin/git", "log", "--pretty=format:%ct", "-1", "HEAD"],
            shell=False, cwd=path,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    except Exception, err:
        return _error("Can't get git hash: %s" % err)

    process.wait()
    returncode = process.returncode
    if returncode != 0:
        return _error(
            "Can't get git hash, returncode was: %r"
            " - git stdout: %r"
            " - git stderr: %r"
            % (returncode, process.stdout.readline(), process.stderr.readline())
        )

    output = process.stdout.readline().strip()
    try:
        timestamp = int(output)
    except Exception, err:
        return _error("git log output is not a number, output was: %r" % output)

    try:
        return time.strftime(".%m%d", time.gmtime(timestamp))
    except Exception, err:
        return _error("can't convert %r to time string: %s" % (timestamp, err))


VERSION_STRING += get_commit_timestamp()


#------------------------------------------------------------------------------


USAGE = """
%prog [OPTIONS] PYLUCID_ENV_DIR DEST
"""

COPYTREE_IGNORE_FILES = (
    '*.pyc', 'tmp*', '.tmp*', "*~",
    "local_settings.py", "*.db3",
    "*.pth", "*.egg", "*.egg-link", "*.egg-info",
    "AUTHORS", "INSTALL", "README.*", "LICENSE", "MANIFEST.in", "setup.*"
)
COPYTREE_IGNORE_DIRS = (
    "dist", "build", "bootstrap", "docs", "extras", "pip", "tests", "scripts",
)

KEEP_ROOT_FILES = (
    "feedparser.py",
)

EXECUTEABLE_FILES = (
    "index.cgi", "index.fcgi", "index.wsgi",
    "install_pylucid.cgi",
    "manage.py",
)

SCRIPT_PATCH_DATA = (
    ('os.environ["VIRTUALENV_FILE"] = ', '# Not needed in standalone package!\n# os.environ["VIRTUALENV_FILE"] = '),
    ('    activate_virtualenv()', '    # Not needed in standalone package!\n    # activate_virtualenv()'),
)

PKG_CHECK_CONTENT = """
# overwritten by %s
# original file can be found here:
# http://github.com/jedie/PyLucid/blob/master/pylucid_project/apps/pylucid/__init__.py
"""

PROJECT_INIT_FILE = '''# coding: utf-8
"""
    PyLucid version string
    ~~~~~~~~~~~~~~~~~~~~~~
    this file was generated with: %s
    original file can be found here:
    http://github.com/jedie/PyLucid/blob/master/pylucid_project/__init__.py
"""
__version__ = %s
VERSION_STRING = "%s"
'''



class CopyTreeError(Exception):
    pass

def copytree2(src, dst, ignore, ignore_path=None):
    """
    similar to shutil.copytree, except:
        + don't copy links as symlinks
        + create destination dir, only if not exist
        + ignore items starts with "." (e.g.: .svn, .git)
    """
    names = os.listdir(src)

    ignored_names = ignore(src, names)

    errors = []

    if not os.path.isdir(dst):
        try:
            os.makedirs(dst)
        except OSError, why:
            errors.extend((dst, str(why)))

    for name in names:
        if name in ignored_names:
            continue
        if name.startswith("."):
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                if ignore_path and name in ignore_path:
                    continue
                copytree2(srcname, dstname, ignore, ignore_path)
            else:
                shutil.copy2(srcname, dstname)
#                print count, srcname
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except CopyTreeError, err:
            errors.extend(err.args[0])

    try:
        shutil.copystat(src, dst)
    except OSError, why:
        errors.extend((src, dst, str(why)))

    if errors:
        raise CopyTreeError(errors)


class ReqInfo(object):
    """
    Information witch paths we must copied.
    Get this information from pylucid's setup.py
    """
    def __init__(self, project_name):
        self.dists = pkg_resources.require(project_name)
        self.paths = self.get_paths()

    def get_paths(self):
        paths = []
        for dist in self.dists:
            path = dist.location
            if path not in paths:
                paths.append(path)
        return paths

    def debug(self):
        for dist in self.dists:
            print "_"*79
            print dist
            print "project_name..:", dist.project_name
            print "location......:", dist.location


class StandalonePackageMaker(object):
    def __init__(self, dest_dir):
        self.dest_dir = self._make_abspath(dest_dir)
        self.dest_package_dir = os.path.join(self.dest_dir, "PyLucid_standalone")

        env_path = os.environ.get("VIRTUAL_ENV")
        if env_path is None:
            print "Error: VIRTUAL_ENV not in environment!"
            print "Have you activate the virtualenv?"
            sys.exit(-1)
        if not os.path.isdir(env_path):
            print "Error: VIRTUAL_ENV path %r doesn't exist?!?!" % env_path
            sys.exit(-1)

        self.pylucid_env_dir = env_path
        self.pylucid_dir = os.path.join(self.pylucid_env_dir, "src", "pylucid")

        self.precheck()

        print "\nuse %r as source" % self.pylucid_env_dir
        print "create standalone package in %r\n" % self.dest_package_dir

        self.pylucid_version = self.get_pylucid_version()
        print "found: PyLucid v%s\n" % self.pylucid_version

        self.req = ReqInfo("pylucid")

        self.check_if_dest_exist()
        self.copy_packages()
        self.cleanup_dest_dir()
        self.create_local_settings()
        self.copy_standalone_script_files()
        self.patch_script_files()
        self.chmod()
        self.remove_pkg_check()
        self.hardcode_version_string()
        self.merge_static_files()

        print
        print "_" * 79
        print "Create 7zip and zip archive files in '%s' ?" % self.dest_dir
        print
        raw_input("(Press any key or abort with Strg-C)")

        archive_file_prefix = os.path.join(self.dest_dir,
            "PyLucid_standalone_%s" % self.pylucid_version.replace(".", "-")
        )
        self.create_archive(archive_file_prefix + ".7z", switches=["-t7z"])
        self.create_archive(archive_file_prefix + ".zip", switches=["-tzip"])

    def _make_abspath(self, path):
        path = os.path.expanduser(path)
        path = os.path.normpath(path)
        path = os.path.abspath(path)
        return path

    def precheck(self):
        if not os.path.isdir(self.pylucid_env_dir):
            print "Wrong PYLUCID_ENV_DIR: %r doesn't exist." % self.pylucid_env_dir
            sys.exit(3)

        test_file = os.path.join(self.pylucid_env_dir, "bin", "activate_this.py")
        if not os.path.isfile(test_file):
            print "Wrong PYLUCID_ENV_DIR: %r doesn't exist." % test_file
            sys.exit(3)

    def get_pylucid_version(self):
        process = subprocess.Popen(
           [os.path.join(self.pylucid_env_dir, "bin", "python"), "setup.py", "--version"],
           cwd=self.pylucid_dir, stdout=subprocess.PIPE
        )
        pylucid_version = process.stdout.readline().strip()
        return pylucid_version

    def check_if_dest_exist(self):
        if os.path.isdir(self.dest_package_dir):
            print "Error: destination dir %r exist!" % self.dest_package_dir
            if raw_input("Delete the entire directory tree? [y/n]").lower() not in ("y", "j"):
                print "Abort!"
                sys.exit(1)

            print "delete tree...",
            shutil.rmtree(self.dest_package_dir)
            print "OK"
            if os.path.isdir(self.dest_package_dir):
                raw_input("Path exist?!?!? continue? (Abort with Strg-C)")
        else:
            raw_input("continue? (Abort with Strg-C)")

    def _patch_file(self, filepath, patch_data):
        print "Patch file %r..." % filepath
        f = codecs.open(filepath, "r", encoding="utf-8")
        content = f.read()
        f.close()

        for placeholder, new_value in patch_data:
            if not placeholder in content:
                print "Warning: String %r not found in %r!" % (placeholder, filepath)
            else:
                content = content.replace(placeholder, new_value)

        f = codecs.open(filepath, "w", encoding="utf-8")
        f.write(content)
        f.close()

    def create_local_settings(self):
        print "_"*79
        print "Create local_settings.py file..."

        sourcepath = os.path.join(self.pylucid_dir, "scripts", "local_settings_example.py")
        destpath = os.path.join(self.dest_package_dir, "local_settings.py")

        print "copy %s -> %s" % (sourcepath, destpath)
        shutil.copy2(sourcepath, destpath)

        secret_key = ''.join(
            [random.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)]
        )
        patch_data = [
            (
                'MEDIA_ROOT = "/var/www/YourSite/media/"',
                'MEDIA_ROOT = os.path.join(os.getcwd(), "media")'
            ),
            (
                'SECRET_KEY = "add-a-secret-key"',
                'SECRET_KEY = "Please change this! %s"' % secret_key
            ),
        ]

        self._patch_file(destpath, patch_data)

    def copy_packages(self):
        for path in self.req.paths:
            print "_" * 79
            print "copy %s" % path

            if not os.path.isdir(path):
                print "Error: %r doesn't exist!" % path
                sys.exit(3)

            print "%s -> %s" % (path, self.dest_package_dir)
            try:
                copytree2(
                    path, self.dest_package_dir,
                    shutil.ignore_patterns(*COPYTREE_IGNORE_FILES),
                    ignore_path=COPYTREE_IGNORE_DIRS
                )
            except OSError, why:
                print "copytree2 error: %s" % why
            else:
                print "OK"

    def cleanup_dest_dir(self):
        print "_"*79
        print "Cleanup dest dir:"
        for filename in os.listdir(self.dest_package_dir):
            path = os.path.join(self.dest_package_dir, filename)
            if not os.path.isfile(path):
                continue
            if filename in KEEP_ROOT_FILES:
                continue
            print "remove: %r (%s)" % (filename, path)
            os.remove(path)

    def copy_standalone_script_files(self):
        print
        print "_" * 79
        print "copy standalone script files"

        def copy_files(scripts_sub_dir):
            src = os.path.join(self.pylucid_dir, "scripts", scripts_sub_dir)
            print "%s -> %s" % (src, self.dest_package_dir)
            try:
                copytree2(src, self.dest_package_dir, ignore=shutil.ignore_patterns(*COPYTREE_IGNORE_FILES))
            except OSError, why:
                print "copytree2 error: %s" % why
            else:
                print "OK"

        copy_files("apache_files")
        copy_files("standalone")

        old = os.path.join(self.dest_package_dir, "default.htaccess")
        new = os.path.join(self.dest_package_dir, ".htaccess")
        print "rename %r to %r" % (old, new)
        os.rename(old, new)

    def patch_script_files(self):
        print
        print "_" * 79
        print "patch script files"
        for filename in ("index.cgi", "index.fcgi", "index.wsgi"):
            filepath = os.path.join(self.dest_package_dir, filename)
            self._patch_file(filepath, SCRIPT_PATCH_DATA)

    def chmod(self):
        print
        print "_" * 79
        print "make files executeable"
        for filename in EXECUTEABLE_FILES:
            filepath = os.path.join(self.dest_package_dir, filename)
            print "chmod 0755 %s" % filepath
            os.chmod(filepath, 0755)

    def remove_pkg_check(self):
        """
        overwrite pylucid_project/apps/pylucid/__init__.py
        and remove pkg_resources.require() check.
        Because it can't work in standalone version
        """
        print
        print "_" * 79
        pylucid_app = os.path.join(self.dest_package_dir, "pylucid_project", "apps", "pylucid")
        pylucid_app_init = os.path.join(pylucid_app, "__init__.py")
        print "Remove pkg_resources.require() check, by overwrite:"
        print pylucid_app_init

        f = open(pylucid_app_init, 'w')
        f.write(PKG_CHECK_CONTENT % __file__)
        f.close()
        print "OK"

    def hardcode_version_string(self):
        """
        Overwrite pylucid version file pylucid_project/__init__.py
        and 'hardcode' complete version string
        """
        print
        print "_" * 79
        version_file = os.path.join(self.dest_package_dir, "pylucid_project", "__init__.py")
        print "'hardcode' PyLucid version string, by overwrite:"
        print version_file

        version_string2 = []
        for part in self.pylucid_version.split("."):
            if part.isdigit():
                part = int(part)
            version_string2.append(part)
        version_string2 = repr(tuple(version_string2))

        f = open(version_file, "w")
        f.write(PROJECT_INIT_FILE % (__file__, version_string2, self.pylucid_version))
        f.close()
        print "OK"

    def cleanup_external_plugins(self):
        print
        print "_" * 79
        print "cleanup external_plugins directory"
        external_plugins = os.path.join(self.dest_package_dir, "pylucid_project", "external_plugins")
        for dir_item in os.listdir(external_plugins):
            if dir_item == "__init__.py":
                continue
            full_path = os.path.join(external_plugins, dir_item)
            print "remove %r..." % full_path,
            shutil.rmtree(full_path)
            print "OK"

    def merge_static_files(self):
        print "_" * 79
        print "move PyLucid/Django static media files together"
        dest_media = os.path.join(self.dest_package_dir, "media")

        pylucid_src_media = os.path.join(self.dest_package_dir, "pylucid_project", "media")
        pylucid_dst_media = os.path.join(dest_media)
        print "move files from %s to %s" % (pylucid_src_media, pylucid_dst_media)
        shutil.move(pylucid_src_media, pylucid_dst_media)
        print "OK"

        django_src_media = os.path.join(self.dest_package_dir, "django", "contrib", "admin", "media")
        django_dst_media = os.path.join(dest_media, "django")
        print "move files from %s to %s" % (django_src_media, django_dst_media)
        shutil.move(django_src_media, django_dst_media)
        print "OK"

    def create_archive(self, archive_file, switches):
        """
        create standalone package archive with 7zip
        needed package is: p7zip-full
        
        FIXME: Can't create a windows exe file with -sfx7z.sfx
        because 7z.sfx doesn't exist in linux version of 7zip :(
        """
        assert isinstance(switches, list)
        if os.path.isfile(archive_file):
            # Delete old archive, otherwise 7zip add new files
            os.remove(archive_file)

        seven_zip = "/usr/bin/7z"
        cmd = [seven_zip, "a", "-mx9"] + switches + [archive_file, self.dest_package_dir]
        print "run:\n%s" % " ".join(cmd)
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        except OSError, err:
            import errno
            if err.errno == errno.ENOENT: # No 2: No such file or directory
                print "Error: '%s' not found: %s" % (seven_zip, err)
                print "Please install it."
                print "e.g.: sudo aptitude install p7zip-full"
                sys.exit(2)
            raise

        while True:
            line = process.stdout.readline()
            if not line:
                break
            line = line.strip()
            if line.startswith("Compressing"):
                line = line[-79:]
                line += " " * (79 - len(line))
                sys.stdout.write('\r' + line)
            else:
                print line

        print "\n-- END --\n"




def main():
    parser = optparse.OptionParser(version=VERSION_STRING, usage=USAGE)
    options, args = parser.parse_args()

    if len(args) != 1:
        print(
            "You must give the destination path as command argument!"
            " (you gave %r)" % repr(args)[1:-1]
        )
        parser.print_help()
        sys.exit(2)

    dest_dir = args[0]
    StandalonePackageMaker(dest_dir)

    print "\n\nPyLucid standalone package created."



if __name__ == '__main__':
    main()
