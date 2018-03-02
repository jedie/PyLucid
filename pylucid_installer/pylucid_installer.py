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
from pathlib import Path

from pylucid.utils import clean_string


SRC_PROJECT_NAME="example_project"

def confirm(txt=None):
    if txt is not None:
        print("\n%s" % txt)
    if input("\nContinue? (Y/N)").lower() not in ("y", "j"):
        print("Bye.")
        sys.exit(-1)


def _check_destination(dest, remove, exist_ok):
    if not dest:
        raise RuntimeError("Path needed!")

    dest = Path(dest).expanduser().resolve() # Already done in pylucid.pylucid_boot.Cmd2()._complete_path()
    if exist_ok:
        return dest

    if dest.is_dir():
        if remove:
            confirm("Delete %r before copy?" % dest)
            print("remove tree %r" % dest)
            shutil.rmtree(dest)
        else:
            raise RuntimeError("ERROR: Destination %r exist!" % dest)

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
    src_base = Path(__file__).parent
    src = Path(src_base, "page_instance_template")
    print("copytree '%s' to '%s'" % (src, dest))
    copytree2(
        src, dest,
        ignore=shutil.ignore_patterns("*.pyc", "__pycache__"),
        exist_ok=exist_ok
    )


def get_python3_shebang():
    executable = sys.executable
    if not executable.endswith("3"):
        executable += "3" # .../bin/python -> .../bin/python3

    shebang="#!%s" % executable
    return shebang


def _patch_shebang(filepath):
    new_shebang=get_python3_shebang()
    print("Update shebang in '%s' to %r" % (filepath, new_shebang))
    with filepath.open("r+") as f:
        content = f.read()
        f.seek(0)

        new_content=content.replace("#!/usr/bin/env python", new_shebang)

        if new_content == content:
            print("WARNING: Shebang not updated in '%s'!" % filepath)
        else:
            f.write(new_content)


def _mass_replace(replace_dict, files):
    for filepath in files:
        print("Update filecontent '%s'" % filepath)
        with open(filepath, "r+") as f:
            content = f.read()

            old_content = content
            for old, new in replace_dict.items():
                if old not in content:
                    print("WARNING: String %r not found!" % old)
                else:
                    content=content.replace(
                        str(old), str(new)  # use str() for pathlib.Path() instance
                    )

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
    confirm()
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
    dest = _check_destination(dest, remove, exist_ok)

    print("Create instance with name %r at: %s..." % (name, dest))

    _copytree(dest, exist_ok)

    _rename_project(dest, name)

    # _mass_replace(
    #     {SRC_PROJECT_NAME: name},
    #     [
    #         Path(dest, name, "templates", "includes", "header.html"),
    #         Path(dest, name, "templates", "includes", "footer.html"),
    #     ]
    # )

    manage_file_path = Path(dest, "manage.py")

    _patch_shebang(filepath=manage_file_path)
    _patch_shebang(filepath=Path(dest, name, "wsgi.py"))

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
            Path(dest, name, "settings.py"),
            manage_file_path
        ]
    )

    print("Page instance created here: '%s'" % dest)
    print("Please change settings,templates etc. for you needs!")
