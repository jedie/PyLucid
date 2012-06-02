#!/bin/bash

# copy this file into: /home/FooBar/PyLucid_env/

function verbose_eval {
    echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    echo $*
    echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    eval $*
    echo
}

echo _____________________________________________________________________
echo activate the virtual environment:
verbose_eval source bin/activate

export DJANGO_SETTINGS_MODULE=pylucid_project.settings
export LOCAL_SETTINGS_MODULE=pylucid_project.management_command_settings

echo _____________________________________________________________________
echo execute manage.py
verbose_eval python src/pylucid/pylucid_project/manage.py create_instance $*

echo ---------------------------------------------------------------------