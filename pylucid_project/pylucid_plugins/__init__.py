"""
Here should be stored all PyLucid plugins.
These plugins are normal django apps.
"""

import os

class PluginList(object):
    """
    needed in settings.py
    """
    _CACHE = None

    def __init__(self, fs_path, pkg_prefix):
        installed_apps = ()
        template_dirs = ()
        for dir_item in os.listdir(fs_path):
            if dir_item.startswith("."):
                continue
            item_path = os.path.join(fs_path, dir_item)
            if not os.path.isdir(item_path):
                continue

            pkg_string = ".".join([pkg_prefix, dir_item])
            installed_apps += (pkg_string,)

            template_path = os.path.join(item_path, "templates")
            if os.path.isdir(template_path):
                template_dirs += (template_path,)

#            admin_url_file = os.path.join(item_path, "admin_url.py")
#            if os.path.isfile(admin_url_file):
#                admin_urls.append(pkg_string + ".admin_url")

        self._CACHE = {
            "installed_apps": installed_apps,
            "template_dirs": template_dirs,
        }

    def get_installed_apps(self):
        return self._CACHE["installed_apps"]
    def get_template_dirs(self):
        return self._CACHE["template_dirs"]
