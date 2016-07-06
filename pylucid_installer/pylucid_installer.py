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

# https://pypi.python.org/pypi/click/
import click

from pylucid_migration.utils import clean_string


SRC_PROJECT_NAME="example_project"


def _check_activated_virtualenv():
    """precheck if we in a activated virtualenv, but should never happen ;)"""
    if not hasattr(sys, 'real_prefix'):
        click.echo("", err=True)
        click.echo("Error: It seems that we are not running in a activated virtualenv!", err=True)
        click.echo("", err=True)
        click.echo("Please activate your environment first, e.g:", err=True)
        click.echo("\t...my_env$ source bin/activate", err=True)
        click.echo("", err=True)
        click.Abort()
    else:
        click.echo("Activated virtualenv detected: %r (%s)" % (sys.prefix, sys.executable))


def _check_destination(dest, remove, exist_ok):
    if not dest:
        raise click.BadParameter("Path needed!")

    dest = os.path.normpath(os.path.abspath(os.path.expanduser(dest)))

    if exist_ok:
        return dest

    if os.path.isdir(dest):
        if remove:
            click.confirm("Delete %r before copy?" % dest, abort=True)
            click.echo("remove tree %r" % dest)
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
    click.echo("copytree %r to %r" % (src, dest))
    copytree2(
        src, dest,
        ignore=shutil.ignore_patterns("*.pyc", "__pycache__"),
        exist_ok=exist_ok
    )


def _patch_shebang(dest, *filepath):
    filepath = os.path.join(dest, *filepath)
    click.echo("Update shebang in %r" % filepath)

    with open(filepath, "r+") as f:
        content = f.read()
        f.seek(0)

        new_content=content.replace("#!/usr/bin/env python", "#!%s" % sys.executable)

        if new_content == content:
            click.echo("WARNING: Shebang not updated in %r!" % filepath, err=True)
        else:
            f.write(new_content)

def _mass_replace(replace_dict, files):
    for filepath in files:
        click.echo("Update filecontent %r" % filepath)
        with open(filepath, "r+") as f:
            content = f.read()

            old_content = content
            for old, new in replace_dict.items():
                if old not in content:
                    click.echo("WARNING: String %r not found!" % old, err=True)
                else:
                    content=content.replace(old, new)

            if content == old_content:
                click.echo("WARNING: File content not changed?!?", err=True)
            else:
                f.seek(0)
                f.truncate()
                f.write(content)

def _clean_project_name(name):
    clean_name = clean_string(name)
    if clean_name == name:
        return name

    click.echo("\nERROR: The given project name is not useable!")
    click.echo("Should i use:\n")
    click.echo("\t%s\n" % clean_name)
    click.confirm("Continue ?", abort=True)
    return clean_name


def _rename_project(dest, name):
    src = os.path.join(dest, SRC_PROJECT_NAME)
    dst = os.path.join(dest, name)
    click.echo("Rename %r to %r" % (src, dst))
    shutil.move(src, dst)



@click.command()
@click.option("dest", '--dest', type=click.Path(),
    prompt="The destionation path for new page instance (You can use --dest=...)",
    help="Destination path for new page instance."
)
@click.option("name", '--name',
    prompt="The name of you project (You can use --name=...)",
    help="Project name (No whitespace!)"
)
@click.option("--remove", is_flag=True,
    help="Delete **all** existing files in destination before copy?",
)
@click.option("--exist_ok", is_flag=True,
    help="Ignore existing destination?",
)
def cli(dest, name, remove, exist_ok):
    """
    CLI to create a page instance.
    """
    _check_activated_virtualenv()

    name = _clean_project_name(name)

    click.echo("Create page instance here: %r" % dest)
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

    click.echo("Page instance created here: %r" % dest)
    click.echo("Please change settings,templates etc. for you needs!")