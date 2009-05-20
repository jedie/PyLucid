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

echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
echo Info:
echo For testing the site Framework, you can start the server with:
echo    ./manage.sh 8000
echo or:
echo    ./manage.sh 8001
echo 
verbose_eval export USED_PORT=$2

echo _____________________________________________________________________
echo execute manage.py
verbose_eval python manage.py $*