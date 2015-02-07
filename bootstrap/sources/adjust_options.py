# coding: utf-8

# imports not really needed and just for the editor warning ;)
import sys
from bootstrap.sources.prefix_code import c, SysPath, get_requirement_choice, CHOICES


def adjust_options(options, args):
    # --- CUT here ---
    """
    Display MENU_TXT
    """
    sys.stderr.write(c.colorize("PyLucid virtual environment bootstrap\n\n", opts=("bold", "underscore")))

    try:
        home_dir = args[0]
    except IndexError:
        return # caller will raise error

    sys.stdout.write("Create PyLucid environment in: %s" % c.colorize(home_dir, foreground="blue", opts=("bold",)))
    sys.stdout.write("\n\n")

    p = SysPath()

    git_path = p.find("git")
    if git_path:
        sys.stderr.write("git found in: %s\n" % c.colorize(git_path, opts=("bold",)))
    else:
        sys.stderr.write(c.colorize("ERROR:", foreground="red", opts=("underscore",)))
        sys.stderr.write("git not found in path!\n")

    if options.install_type == None:
        options.install_type = get_requirement_choice()
    elif options.install_type not in CHOICES.values():
        sys.stderr.write("install type wrong!")
        sys.exit(-1)

    # sys.stdout.write("options: %s\n" % repr(options))
    # sys.stdout.write("args: %s\n" % repr(args))