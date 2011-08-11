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


__version__ = (0, 1, 0, 'alpha')


VERSION_STRING = '.'.join(str(part) for part in __version__)


try:
    process = subprocess.Popen(
       ["git", "log", "--format='%h'", "-1", "HEAD"],
       stdout=subprocess.PIPE
    )
except Exception, err:
    warnings.warn("Can't get git hash: %s" % err)
else:
    process.wait()
    returncode = process.returncode
    if returncode == 0:
        output = process.stdout.readline().strip().strip("'")
        if len(output) != 7:
            warnings.warn("Can't get git hash, output was: %r" % output)
        else:
            VERSION_STRING += ".git-%s" % output
    else:
        warnings.warn("Can't get git hash, returncode was: %s" % returncode)

USAGE = """
%prog [OPTIONS] PYLUCID_ENV_DIR DEST
"""

COPYTREE_IGNORE = (
    '*.pyc', 'tmp*', '.tmp*', "*~",
    ".svn", ".git", ".project", ".pydev*",
    "local_settings.py", "*.db3",
    "*.egg-info",
)

EXECUTEABLE_FILES = (
    "index.cgi", "index.fcgi",
    "install_pylucid.cgi",
    "manage.py",
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
        + ignore directories starts with "." (e.g.: .svn, .git)
        + ignore full path
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
        srcname = os.path.join(src, name)
        if ignore_path and srcname in ignore_path:
            continue
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                copytree2(srcname, dstname, ignore, ignore_path)
            else:
                shutil.copy2(srcname, dstname)
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




class StandalonePackageMaker(object):
    def __init__(self, pylucid_env_dir, dest_dir):
        self.dest_dir = os.path.abspath(dest_dir)
        self.dest_package_dir = os.path.join(self.dest_dir, "PyLucid_standalone")
        self.pylucid_env_dir = os.path.abspath(pylucid_env_dir)
        self.pylucid_dir = os.path.join(self.pylucid_env_dir, "src", "pylucid")

        self.precheck()

        print "\nuse %r as source" % self.pylucid_env_dir
        print "create standalone package in %r\n" % self.dest_package_dir

        self.pylucid_version = self.get_pylucid_version()
        print "found: PyLucid v%s\n" % self.pylucid_version

        self.check_if_dest_exist()
        self.copy_packages()
        self.copy_standalone_script_files()
        self.chmod()
        self.remove_pkg_check()
        self.hardcode_version_string()
        self.merge_static_files()
        self.copy_wsgiref()

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

    def copy_packages(self):
        lib_dir = os.path.join(self.pylucid_env_dir, "lib")
        lib_sub_dirs = os.listdir(lib_dir)
        if len(lib_sub_dirs) != 1:
            print "Error: Wrong sub dirs in %r" % lib_dir
            sys.exist(3)

        python_lib_dir = lib_sub_dirs[0]
        if not python_lib_dir.startswith("python"):
            print "Error: %r doesn't start with python!" % python_lib_dir
            sys.exist(3)

        site_packages_dir = os.path.join(lib_dir, python_lib_dir, "site-packages")

        dirs_to_copy = [
            ("PyLucid", os.path.join(self.pylucid_dir, "pylucid_project")),
            ("Django", os.path.join(self.pylucid_env_dir, "src", "django", "django")),
            ("dbpreferences", os.path.join(self.pylucid_env_dir, "src", "dbpreferences", "dbpreferences")),
            ("django-tools", os.path.join(self.pylucid_env_dir, "src", "django-tools", "django_tools")),
            ("python-creole", os.path.join(self.pylucid_env_dir, "src", "python-creole", "creole")),

            ("django-dbtemplates", os.path.join(site_packages_dir, "dbtemplates")),
            ("django-reversion", os.path.join(site_packages_dir, "reversion")),
            ("django-tagging", os.path.join(site_packages_dir, "tagging")),

            ("Pygments", os.path.join(site_packages_dir, "pygments")),
        ]
        files_to_copy = [
            ("feedparser", os.path.join(site_packages_dir, "feedparser.py")),
        ]

        for dir_info in dirs_to_copy:
            if not os.path.isdir(dir_info[1]):
                print "Error: %r doesn't exist!" % dir_info[1]
                sys.exist(3)

        for file_info in files_to_copy:
            if not os.path.isfile(file_info[1]):
                print "Error: file %r not found!" % file_info[1]
                sys.exist(3)

        #----------------------------------------------------------------------
        print

        # Don't copy existing external_plugins and not local test plugins ;)
        ignore_path = []
        external_plugins = os.path.join(self.pylucid_dir, "pylucid_project", "external_plugins")
        for dir_item in os.listdir(external_plugins):
            if dir_item == "__init__.py":
                continue
            full_path = os.path.join(external_plugins, dir_item)
            ignore_path.append(full_path)

        # Copy only PyLucid media files and not local test files ;)
        media_path = os.path.join(self.pylucid_dir, "pylucid_project", "media")
        for dir_item in os.listdir(media_path):
            if dir_item == "PyLucid":
                continue
            full_path = os.path.join(media_path, dir_item)
            ignore_path.append(full_path)

        for package_name, path in dirs_to_copy:
            print "_" * 79
            print "copy %s" % package_name
            package_dest = os.path.join(self.dest_package_dir, os.path.split(path)[1])
            print "%s -> %s" % (path, package_dest)
            try:
                files_copied = copytree2(
                    path, package_dest,
                    shutil.ignore_patterns(*COPYTREE_IGNORE), ignore_path
                )
            except OSError, why:
                print "copytree2 error: %s" % why
            else:
                print "OK"

        #----------------------------------------------------------------------
        print

        for module_name, path in files_to_copy:
            print "_" * 79
            print "copy %s" % module_name
            print "%s -> %s" % (path, self.dest_package_dir)
            try:
                shutil.copy2(path, self.dest_package_dir)
            except OSError, why:
                print "copy error: %s" % why
            else:
                print "OK"

    def copy_standalone_script_files(self):
        print
        print "_" * 79
        print "copy standalone script files"
        src = os.path.join(self.pylucid_dir, "scripts", "standalone")
        print "%s -> %s" % (src, self.dest_package_dir)
        try:
            copytree2(src, self.dest_package_dir, ignore=shutil.ignore_patterns(*COPYTREE_IGNORE))
        except OSError, why:
            print "copytree2 error: %s" % why
        else:
            print "OK"

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

    def copy_wsgiref(self):
        print
        print "_" * 79
        import wsgiref
        print "copy wsgiref"
        wsgiref_src = os.path.abspath(os.path.dirname(wsgiref.__file__))
        wsgiref_dst = os.path.join(self.dest_package_dir, "wsgiref")
        print "%s -> %s" % (wsgiref_src, wsgiref_dst)
        copytree2(wsgiref_src, wsgiref_dst, ignore=shutil.ignore_patterns("*.pyc", "*.pyo"))

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

        print "OK"




def main():
    parser = optparse.OptionParser(version=VERSION_STRING, usage=USAGE)
    options, args = parser.parse_args()

    args = (os.path.expanduser("~/PyLucid_env"), os.path.expanduser("~/servershare"))

    if len(args) != 2:
        print(
            "You must give two arguments: PYLUCID_ENV_DIR and DEST"
            " (you gave %s)" % repr(args)[1:-1]
        )
        parser.print_help()
        sys.exit(2)

    pylucid_env_dir = args[0]
    dest_dir = args[1]
    StandalonePackageMaker(pylucid_env_dir, dest_dir)

    print "\n\nPyLucid standalone package created."



if __name__ == '__main__':
    main()
