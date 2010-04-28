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
    '*.pyc', 'tmp*',
    ".svn", ".git",
    "local_settings.py", "*.db3",
    "*.egg-info",
)

class CopyTreeError(Exception):
    pass

def copytree2(src, dst, ignore):
    """
    similar to shutil.copytree, except:
        + don't copy links as symlinks
        + create destination dir, only if not exist
        + ignore directories starts with "." (e.g.: .svn, .git)
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
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                copytree2(srcname, dstname, ignore)
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
    except WindowsError:
        # can't copy file access times on Windows
        pass
    except OSError, why:
        errors.extend((src, dst, str(why)))

    if errors:
        raise CopyTreeError(errors)






def create_standalone_package(pylucid_env_dir, dest_dir):
    dest_dir = os.path.join(os.path.abspath(dest_dir), "PyLucid_standalone_package")
    pylucid_env_dir = os.path.abspath(pylucid_env_dir)
    if not os.path.isdir(pylucid_env_dir):
        print "Wrong PYLUCID_ENV_DIR: %r doesn't exist." % pylucid_env_dir
        sys.exit(3)

    test_file = os.path.join(pylucid_env_dir, "bin", "activate_this.py")
    if not os.path.isfile(test_file):
        print "Wrong PYLUCID_ENV_DIR: %r doesn't exist." % test_file
        sys.exit(3)

    print "\nuse %r as source" % pylucid_env_dir
    print "create standalone package in %r\n" % dest_dir

#    raw_input("continue? (Abort with Strg-C)")

    lib_dir = os.path.join(pylucid_env_dir, "lib")
    lib_sub_dirs = os.listdir(lib_dir)
    if len(lib_sub_dirs) != 1:
        print "Error: Wrong sub dirs in %r" % lib_dir
        sys.exist(3)

    python_lib_dir = lib_sub_dirs[0]
    if not python_lib_dir.startswith("python"):
        print "Error: %r doesn't start with python!" % python_lib_dir
        sys.exist(3)

    site_packages_dir = os.path.join(lib_dir, python_lib_dir, "site-packages")
    pylucid_dir = os.path.join(pylucid_env_dir, "src", "pylucid")

    dirs_to_copy = [
        ("PyLucid", os.path.join(pylucid_dir, "pylucid_project")),
        ("Django", os.path.join(pylucid_env_dir, "src", "django", "django")),
        ("dbpreferences", os.path.join(pylucid_env_dir, "src", "dbpreferences", "dbpreferences")),
        ("django-tools", os.path.join(pylucid_env_dir, "src", "django-tools", "django_tools")),
        ("python-creole", os.path.join(pylucid_env_dir, "src", "python-creole", "creole")),

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

    for package_name, path in dirs_to_copy:
        print "_" * 79
        print "copy %s" % package_name
        package_dest = os.path.join(dest_dir, os.path.split(path)[1])
        print "%s -> %s" % (path, package_dest)
        try:
            files_copied = copytree2(path, package_dest, ignore=shutil.ignore_patterns(*COPYTREE_IGNORE))
        except OSError, why:
            print "copytree2 error: %s" % why

    for module_name, path in files_to_copy:
        print "_" * 79
        print "copy %s" % module_name
        print "%s -> %s" % (path, dest_dir)
        shutil.copy2(path, dest_dir)

    print "_" * 79
    print "copy standalone script files"
    src = os.path.join(pylucid_dir, "scripts", "standalone")
    print "%s -> %s" % (src, dest_dir)
    try:
        copytree2(src, dest_dir, ignore=shutil.ignore_patterns(*COPYTREE_IGNORE))
    except OSError, why:
        print "copytree2 error: %s" % why


def main():
    parser = optparse.OptionParser(version=VERSION_STRING, usage=USAGE)
    options, args = parser.parse_args()

    if len(args) != 2:
        print(
            "You must give two arguments: PYLUCID_ENV_DIR and DEST"
            " (you gave %s)" % repr(args)[1:-1]
        )
        parser.print_help()
        sys.exit(2)

    pylucid_env_dir = args[0]
    dest_dir = args[1]
    create_standalone_package(pylucid_env_dir, dest_dir)

    print "\n\nPyLucid standalone package created."



if __name__ == '__main__':
    main()
