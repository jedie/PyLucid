
# Bootstrap-Env
from bootstrap_env.admin_shell.path_helper import PathHelper

# PyLucid
import pylucid


def get_path_helper_instance():
    base_file = pylucid.__file__
    print("\nbootstrap_env.__file__: %r\n" % base_file)

    path_helper = PathHelper(
        base_file=base_file,
        boot_filename="pylucid_boot.py",
        admin_filename="pylucid_admin.py",
    )
    return path_helper


if __name__ == '__main__':
    path_helper = get_path_helper_instance()
    path_helper.print_path()
    path_helper.assert_all_path()
