#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid installer
    ~~~~~~~~~~~~~~~~~

    CLI to create a page instance

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys
import shutil
import random
import string


from pylucid.utils import clean_string


SRC_PROJECT_NAME="example_project"


def _check_activated_virtualenv():
    """precheck if we in a activated virtualenv, but should never happen ;)"""
    if not hasattr(sys, 'real_prefix'):
        print("")
        print("Error: It seems that we are not running in a activated virtualenv!")
        print("")
        print("Please activate your environment first, e.g:")
        print("\t...my_env$ source bin/activate")
        print("")
        click.Abort()
    else:
        print("Activated virtualenv detected: %r (%s)" % (sys.prefix, sys.executable))


def _check_destination(dest, remove, exist_ok):
    if not dest:
        raise click.BadParameter("Path needed!")

    dest = os.path.normpath(os.path.abspath(os.path.expanduser(dest)))

    if exist_ok:
        return dest

    if os.path.isdir(dest):
        if remove:
            click.confirm("Delete %r before copy?" % dest, abort=True)
            print("remove tree %r" % dest)
            shutil.rmtree(dest)
        else:
            raise click.BadParameter("ERROR: Destination %r exist! (Maybe use '--exist_ok')" % dest)

    return dest

def copytree2(src, dst, ignore, exist_ok=False):
    """
    Similar to shutil.copytree, but has 'exist_ok'
    """
    names = os.listdir(src)
    ignored_names = ignore(src, names)

    os.makedirs(dst, exist_ok=exist_ok)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                copytree2(srcname, dstname, ignore, exist_ok=exist_ok)
            else:
                # Will raise a SpecialFileError for unsupported file types
                shutil.copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        shutil.copystat(src, dst)
    except OSError as why:
        # Copying file access times may fail on Windows
        if getattr(why, 'winerror', None) is None:
            errors.append((src, dst, str(why)))

    if errors:
        raise OSError(errors)
    return dst


def _copytree(dest, exist_ok):
    src_base = os.path.abspath(os.path.dirname(__file__))
    src = os.path.join(src_base, "page_instance_template")
    print("copytree %r to %r" % (src, dest))
    copytree2(
        src, dest,
        ignore=shutil.ignore_patterns("*.pyc", "__pycache__"),
        exist_ok=exist_ok
    )


def _patch_shebang(dest, *filepath):
    filepath = os.path.join(dest, *filepath)
    print("Update shebang in %r" % filepath)

    with open(filepath, "r+") as f:
        content = f.read()
        f.seek(0)

        new_content=content.replace("#!/usr/bin/env python", "#!%s" % sys.executable)

        if new_content == content:
            print("WARNING: Shebang not updated in %r!" % filepath)
        else:
            f.write(new_content)

def _mass_replace(replace_dict, files):
    for filepath in files:
        print("Update filecontent %r" % filepath)
        with open(filepath, "r+") as f:
            content = f.read()

            old_content = content
            for old, new in replace_dict.items():
                if old not in content:
                    print("WARNING: String %r not found!" % old)
                else:
                    content=content.replace(old, new)

            if content == old_content:
                print("WARNING: File content not changed?!?")
            else:
                f.seek(0)
                f.truncate()
                f.write(content)

def _clean_project_name(name):
    clean_name = clean_string(name)
    if clean_name == name:
        return name

    print("\nERROR: The given project name is not useable!")
    print("Should i use:\n")
    print("\t%s\n" % clean_name)
    click.confirm("Continue ?", abort=True)
    return clean_name


def _rename_project(dest, name):
    src = os.path.join(dest, SRC_PROJECT_NAME)
    dst = os.path.join(dest, name)
    print("Rename %r to %r" % (src, dst))
    shutil.move(src, dst)



def create_instance(dest, name, remove, exist_ok):
    """
    create a page instance.
    """
    name = _clean_project_name(name)

    print("Create page instance here: %r" % dest)
    dest = _check_destination(dest, remove, exist_ok)

    _copytree(dest, exist_ok)

    _rename_project(dest, name)

    _mass_replace(
        {SRC_PROJECT_NAME: name},
        [
            os.path.join(dest, name, "templates", "includes", "header.html"),
            os.path.join(dest, name, "templates", "includes", "footer.html"),
        ]
    )
    _mass_replace(
        {
            "#!/usr/bin/env python": "#!%s" % sys.executable,
            SRC_PROJECT_NAME: name,
        },
        [
            os.path.join(dest, "manage.py"),
            os.path.join(dest, name, "wsgi.py"),
        ]
    )

    secret_key = ''.join(
        [random.choice(string.ascii_letters+string.digits+"!@#$%^&*(-_=+)") for i in range(64)]
    )
    _mass_replace(
        {
            "/path/to/page_instance/": dest,
            SRC_PROJECT_NAME: name,
            'SECRET_KEY = "CHANGE ME!!!"': 'SECRET_KEY = "%s"' % secret_key,
        },
        [
            os.path.join(dest, name, "settings.py"),
        ]
    )

    print("Page instance created here: %r" % dest)
    print("Please change settings,templates etc. for you needs!")
