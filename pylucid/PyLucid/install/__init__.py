
"""
setup for the dynamic _install section menu
look at PyLucid.install.index.menu
"""

import install, tests, low_level_admin, update

__all__ = [install, tests, low_level_admin, update]

SKIP_MODULES = ("index", "BaseInstall")