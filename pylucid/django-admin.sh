#!/bin/sh

#export DJANGO_SETTINGS_MODULE=PyLucid.settings

# use the local django packages
export PYTHONPATH=${PWD}

python ./django/bin/django-admin.py --settings=PyLucid.settings $*