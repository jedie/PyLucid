#!/bin/bash

# for makemessages/compilemessages
# see: http://www.pylucid.org/permalink/314/how-to-localize-pylucid

(
    set -x
    export DJANGO_SETTINGS_MODULE=pylucid_project.settings
    django-admin.py $*
)