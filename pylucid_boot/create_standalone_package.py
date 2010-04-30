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
    dest_dir = os.path.abspath(dest_dir)
    dest_package_dir = os.path.join(dest_dir, "PyLucid_standalone")
    pylucid_env_dir = os.path.abspath(pylucid_env_dir)
    if not os.path.isdir(pylucid_env_dir):
        print "Wrong PYLUCID_ENV_DIR: %r doesn't exist." % pylucid_env_dir
        sys.exit(3)

    test_file = os.path.join(pylucid_env_dir, "bin", "activate_this.py")
    if not os.path.isfile(test_file):
        print "Wrong PYLUCID_ENV_DIR: %r doesn't exist." % test_file
        sys.exit(3)

    print "\nuse %r as source" % pylucid_env_dir
    print "create standalone package in %r\n" % dest_package_dir

    #~/PyLucid_env/src/pylucid$ ./setup.py --version
    pylucid_dir = os.path.join(pylucid_env_dir, "src", "pylucid")

    process = subprocess.Popen(
       [os.path.join(pylucid_env_dir, "bin", "python"), "setup.py", "--version"],
       cwd=pylucid_dir, stdout=subprocess.PIPE
    )
    pylucid_version = process.stdout.readline().strip()
    print "found: PyLucid v%s" % pylucid_version

    print

    if os.path.isdir(dest_package_dir):
        print "Error: destination dir %r exist!" % dest_package_dir
        if raw_input("Delete the entire directory tree? [y/n]").lower() not in ("y", "j"):
            print "Abort!"
            sys.exit(1)

        print "delete tree...",
        shutil.rmtree(dest_package_dir)
        print "OK"
        if os.path.isdir(dest_package_dir):
            raw_input("Path exist?!?!? continue? (Abort with Strg-C)")
    else:
        raw_input("continue? (Abort with Strg-C)")

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

    #--------------------------------------------------------------------------
    print

    for package_name, path in dirs_to_copy:
        print "_" * 79
        print "copy %s" % package_name
        package_dest = os.path.join(dest_package_dir, os.path.split(path)[1])
        print "%s -> %s" % (path, package_dest)
        try:
            files_copied = copytree2(path, package_dest, ignore=shutil.ignore_patterns(*COPYTREE_IGNORE))
        except OSError, why:
            print "copytree2 error: %s" % why
        else:
            print "OK"

    #--------------------------------------------------------------------------
    print

    for module_name, path in files_to_copy:
        print "_" * 79
        print "copy %s" % module_name
        print "%s -> %s" % (path, dest_package_dir)
        try:
            shutil.copy2(path, dest_package_dir)
        except OSError, why:
            print "copy error: %s" % why
        else:
            print "OK"

    #--------------------------------------------------------------------------
    print

    print "_" * 79
    print "copy standalone script files"
    src = os.path.join(pylucid_dir, "scripts", "standalone")
    print "%s -> %s" % (src, dest_package_dir)
    try:
        copytree2(src, dest_package_dir, ignore=shutil.ignore_patterns(*COPYTREE_IGNORE))
    except OSError, why:
        print "copytree2 error: %s" % why
    else:
        print "OK"

    #--------------------------------------------------------------------------
    print

    # overwrite pylucid_project/apps/pylucid/__init__.py
    # and remove pkg_resources.require() check.
    # Because it can't work in standalone version
    pylucid_app = os.path.join(dest_package_dir, "pylucid_project", "apps", "pylucid")
    pylucid_app_init = os.path.join(pylucid_app, "__init__.py")
    print "Remove pkg_resources.require() check, by overwrite:"
    print pylucid_app_init

    f = open(pylucid_app_init, 'w')
    f.write("""# overwritten by %s
# original file can be found here:
# http://github.com/jedie/PyLucid/blob/master/pylucid_project/apps/pylucid/__init__.py
""" % __file__)
    f.close()
    print "OK"

    #--------------------------------------------------------------------------
    print

    # Overwrite pylucid version file pylucid_project/__init__.py
    # and 'hardcode' complete version string
    version_file = os.path.join(dest_package_dir, "pylucid_project", "__init__.py")
    print "'hardcode' PyLucid version string, by overwrite:"
    print version_file

    version_string2 = []
    for part in pylucid_version.split("."):
        if part.isdigit():
            part = int(part)
        version_string2.append(part)
    version_string2 = repr(tuple(version_string2))

    f = open(version_file, "w")
    f.write('''# coding: utf-8
"""
    PyLucid version string
    ~~~~~~~~~~~~~~~~~~~~~~
    this file was generated with: %s
    original file can be found here:
    http://github.com/jedie/PyLucid/blob/master/pylucid_project/__init__.py
"""
__version__ = %s
VERSION_STRING = "%s"
''' % (
        __file__,
        version_string2,
        pylucid_version,
    ))
    f.close()
    print "OK"

    #--------------------------------------------------------------------------
    print

    print "_" * 79
    print "Create 7zip and zip archive files in '%s' ?" % dest_dir
    print
    raw_input("(Press any key or abort with Strg-C)")

    archive_file_prefix = os.path.join(dest_dir, "PyLucid_standalone_%s" % pylucid_version.replace(".", "-"))

    create_archive(archive_file_prefix + ".7z", dest_package_dir, switches=["-t7z"])
    create_archive(archive_file_prefix + ".zip", dest_package_dir, switches=["-tzip"])


def create_archive(archive_file, dest_package_dir, switches):
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
    cmd = [seven_zip, "a", "-mx9"] + switches + [archive_file, dest_package_dir]
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
