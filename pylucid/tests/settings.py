# coding: utf-8

"""
    PyLucid
    ~~~~~~~

    :copyleft: 2015-2018 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from pylucid_page_instance.settings import *  # @UnusedWildImport


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ":memory:"
    }
}
# CACHES['default']= {
#     'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#     'LOCATION': 'default-cache',
#     'TIMEOUT': 60 * 60 * 24, # 24 hours
# }
