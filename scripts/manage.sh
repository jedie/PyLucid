#!/bin/bash

function verbose_eval {
    echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    echo $*
    echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    eval $*
    echo ---------------------------------------------------------------------
    echo
}

echo _____________________________________________________________________
echo activate the virtual environment:
verbose_eval source bin/activate

echo _____________________________________________________________________
echo Go into source folder:
verbose_eval cd src/pylucid/pylucid_project/

echo _____________________________________________________________________
echo execute manage.py
verbose_eval python manage.py $*