
"""
    PyLucid Developer Admin Shell
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :created: 2018 by Jens Diemer
    :copyleft: 2018 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import re
import subprocess
from pathlib import Path

# https://github.com/jedie/bootstrap_env
import bootstrap_env
from bootstrap_env.utils.cookiecutter_utils import verbose_cookiecutter

# PyLucid
import pylucid
from pylucid.admin_shell.normal_shell import VERSION_PREFIXES, PyLucidNormalShell
from pylucid.pylucid_boot import VerboseSubprocess


class PyLucidDeveloperShell(PyLucidNormalShell):
    """
    Expand admin shell with developer commands.
    """

    def do_upgrade_requirements(self, arg, timeout=(3*60)):
        """
        1. Convert via 'pip-compile' *.in requirements files to *.txt
        2. Append 'piprot' informations to *.txt requirements.

        Direct start with:
            $ pylucid_admin upgrade_requirements
        """
        requirement_filepath = self.path_helper.req_filepath # .../pylucid/requirements/developer_installation.txt

        assert requirement_filepath.is_file(), "File not found: '%s'" % requirement_filepath

        requirements_path = requirement_filepath.parent

        count = 0
        for requirement_in in requirements_path.glob("*.in"):
            count +=1
            requirement_in = Path(requirement_in).name

            if requirement_in.startswith("basic_"):
                continue

            requirement_out = requirement_in.replace(".in", ".txt")

            self.stdout.write("_"*79 + "\n")

            # We run pip-compile in ./requirements/ and add only the filenames as arguments
            # So pip-compile add no path to comments ;)

            return_code = VerboseSubprocess(
                "pip-compile", "--verbose", "--upgrade", "-o", requirement_out, requirement_in,
                cwd=str(requirements_path),
                timeout=timeout
            ).verbose_call(check=True)

            if not requirement_in.startswith("test_"):
                req_out = Path(requirements_path, requirement_out)
                with req_out.open("r") as f:
                    requirement_out_content = f.read()

                for version_prefix in VERSION_PREFIXES:
                    if not version_prefix in requirement_out_content:
                        raise RuntimeError("ERROR: %r not found!" % version_prefix)

            #
            # Skip piprot until https://github.com/sesh/piprot/issues/73 fixed
            #
            #
            # self.stdout.write("_"*79 + "\n")
            # output = [
            #     "\n#\n# list of out of date packages made with piprot:\n#\n"
            # ]
            # sp=VerboseSubprocess("piprot", "--outdated", requirement_out, cwd=str(requirements_path))
            # for line in sp.iter_output():
            #     print(line, end="", flush=True)
            #     output.append("# %s" % line)
            #
            # self.stdout.write("\nUpdate file %r\n" % requirement_out)
            # filepath = Path(requirements_path, requirement_out).resolve()
            # assert filepath.is_file(), "File not exists: %r" % filepath
            # with open(filepath, "a") as f:
            #     f.writelines(output)

        if count==0:
            print("ERROR: no *.in files found in: '%s'" % requirements_path)
        else:
            print("processed %i *.in files" % count)


    def do_change_editable_address(self, arg):
        """
        Replace git remote url from github read-only 'https' to 'git@'
        e.g.:

        OLD: https://github.com/jedie/PyLucid.git
        NEW: git@github.com:jedie/PyLucid.git

        **This is only developer with github write access ;)**

        git remote set-url origin https://github.com/jedie/python-creole.git

        Direct start with:
            $ pylucid_admin change_editable_address
        """
        src_path = self.path_helper.src_path  # Path instance pointed to 'src' directory
        for p in src_path.iterdir():
            if not p.is_dir():
                continue

            if str(p).endswith(".bak"):
                continue

            print("\n")
            print("*"*79)
            print("Change: %s..." % p)

            try:
                output = VerboseSubprocess(
                    "git", "remote", "-v",
                    cwd=str(p),
                ).verbose_output(check=False)
            except subprocess.CalledProcessError:
                print("Skip.")
                continue

            (name, url) = re.findall(r"(\w+?)\s+([^\s]*?)\s+", output)[0]
            print("Change %r url: %r" % (name, url))

            new_url=url.replace("https://github.com/", "git@github.com:")
            if new_url == url:
                print("ERROR: url not changed!")
                continue

            VerboseSubprocess("git", "remote", "set-url", name, new_url, cwd=str(p)).verbose_call(check=False)
            VerboseSubprocess("git", "remote", "-v", cwd=str(p)).verbose_call(check=False)

    def do_update_own_boot_file(self, arg):
        """
        Update 'bootstrap_env/boot_bootstrap_env.py' via cookiecutter.

        Only useable on develop installation!

        direct call, e.g.:
        $ pylucid_admin update_own_boot_file
        """
        from packaging.version import parse

        # https://packaging.pypa.io/en/latest/version/
        parsed_pylucid_version = parse(pylucid.__version__)

        if parsed_pylucid_version.is_prerelease:
            print("PyLucid v%s is pre release" % parsed_pylucid_version)
            use_pre_release = "y"
        else:
            print("PyLucid v%s is not a pre release" % parsed_pylucid_version)
            use_pre_release = "n"

        bootstrap_env_path = Path(bootstrap_env.__file__).parent
        assert bootstrap_env_path.is_dir()

        repro_path = Path(bootstrap_env_path, "boot_source")

        output_dir = Path(pylucid.__file__)     # .../PyLucid-env/src/pylucid/pylucid/__init__.py
        output_dir = output_dir.parent          # .../PyLucid-env/src/pylucid/pylucid/
        output_dir = output_dir.parent          # .../PyLucid-env/src/pylucid/

        from cookiecutter.log import configure_logger
        configure_logger(stream_level='DEBUG')

        from bootstrap_env.version import __version__ as bootstrap_env_version

        result = verbose_cookiecutter(
            template=str(repro_path),
            no_input=True,
            overwrite_if_exists=True,
            output_dir=str(output_dir),
            extra_context={
                # see: bootstrap_env/boot_source/cookiecutter.json
                "_version": bootstrap_env_version,
                "project_name": "pylucid",
                "package_name": "pylucid",
                "bootstrap_filename": "pylucid_boot",
                "editable_url": "git+https://github.com/jedie/PyLucid.git@master",
                "raw_url": "https://raw.githubusercontent.com/jedie/PyLucid/master",
                "use_pre_release": use_pre_release,
            },
        )
        print("\nbootstrap file created here: %s" % result)
