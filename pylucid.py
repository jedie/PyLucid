#!/usr/bin/python3

"""
    PyLucid Manage CLI
    ~~~~~~~~~~~~~~~~~~

    :created: 08.02.2018 by Jens Diemer, www.jensdiemer.de
    :copyleft: 2018 by the PyLucid team, see AUTHORS for more details.
    :license: GNU General Public License v3 or later (GPLv3+), see LICENSE for more details.
"""

__version__ = "0.0.1"

import argparse
import logging
import os
import sys

if sys.version_info < (3, 5):
    print("\nERROR: Python 3.5 or greater is required!\n")
    sys.exit(101)


try:
    import readline
except ImportError as err:
    print("\nERROR: no readline available: %s" % err)
    sys.exit(101)


log = logging.getLogger(__name__)



class Command:
    def __init__(self, func, help_text, is_alias=False, **kwargs):
        self.func = func
        self.help_text = help_text
        self.is_alias = is_alias
        self.kwargs = kwargs

    def call(self):
        return self.func(**self.kwargs)


class CommandRegistry:
    def __init__(self):
        self.registry = {}

    def register(self, func=None, help_text="", **kwargs):
        def inner(func):
            aliases = kwargs.pop("aliases", [])
            key = kwargs.pop("key", func.__name__)

            assert key not in self.registry
            self.registry[key] = Command(func, help_text, **kwargs)

            for alias in aliases:
                self.registry[alias] = Command(func, help_text, is_alias=True, **kwargs)

            return func

        if func is None:
            return inner
        else:
            return inner(func)

    def execute(self, func_name):
        command = self.registry[func_name]
        return command.call()


command_registry = CommandRegistry()
register_command = command_registry.register


@register_command(help_text="Update version information in requirements.txt via pip-compile")
def upgrade_requirements():
    print("TODO: upgrade_requirements")


@register_command(help_text="Execute pip/pip-sync with informations from requirements.txt")
def install_requirements():
    print("TODO: install_requirements")


@register_command(help_text="exit interactive shell", key="quit", aliases=("q",))
def quit_shell():
    print("\nbye...")
    sys.exit(0)


@register_command(help_text="help about all existing commands", key="help", aliases=("?",))
def print_help():
    for func_name, command in sorted(command_registry.registry.items()):
        if not command.is_alias: # Skip alias entries ;)
            print("    %-25s: %s" % (func_name, command.help_text))


class InteractiveShell:
    def __init__(self):
        self.pwd_ = ["PyLucid"]
        self._command_keys=command_registry.registry.keys()

        if 'libedit' in readline.__doc__:
            # Mac issues with binding when using tabs for autocompletion
            readline.parse_and_bind("bind -e")
            readline.parse_and_bind("bind '\t' rl_complete")
        else:
            readline.parse_and_bind("tab: complete")

        readline.parse_and_bind("tab: complete")
        readline.set_completer_delims("\t")
        readline.set_completer(self.readline_completer)

    def readline_completer(self, text, state):
        for cmd in self._command_keys:
            if cmd.startswith(text):
                if not state:
                    return cmd
                else:
                    state -= 1

    def pwd(self):
        return "-".join(self.pwd_)+"> "

    def run(self):
        while True:
            try:
                cmd = input(self.pwd())
            except (KeyboardInterrupt, EOFError):
                print("\n\nbye")
                break

            if cmd not in self._command_keys:
                print("%r is not a valid command!" % cmd)
                print("all existing commands are:")
                print(", ".join(self._command_keys))
            else:
                command_registry.execute(cmd)


def main(args=None):
    python_version_info="Python v{}".format(".".join([str(i) for i in sys.version_info]))

    program_name = os.path.basename(__file__)
    parser = argparse.ArgumentParser(
        prog=program_name,
        description="PyLucid Manage cli tool v{} - {}".format(__version__, python_version_info),
        epilog="""created by Jens Diemer, www.jensdiemer.de
            copyleft 2018 by the PyLucid team, see AUTHORS for more details.
            license GNU General Public License v3 or later (GPLv3+), see LICENSE for more details.
            https://www.pylucid.org
        """,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, allow_abbrev=True
    )
    parser.add_argument("--version", action="version", version=__version__)
    parsed_args = parser.parse_args(args)
    log.debug("parsed args: %s", parsed_args)

    InteractiveShell().run()


if __name__ == "__main__":
    main()
