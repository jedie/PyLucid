#!/bin/bash

# pip
# ${BIN}/python ${BIN}/pip install --help

function verbose_eval {
    echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    echo $*
    echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    eval $*
    echo ---------------------------------------------------------------------
    echo
}

PYLUCID_ENV=PyLucid_env
BIN=${PYLUCID_ENV}/bin

# This script created by scripts/create_bootstrap_script.py
BOOTSTRAP_SCRIPT=scripts/pylucid-boot.py

echo _____________________________________________________________________
echo Create virtual environment:
verbose_eval python ${BOOTSTRAP_SCRIPT} ${PYLUCID_ENV}

echo _____________________________________________________________________
echo activate the virtual environment:
verbose_eval source ${BIN}/activate

echo _____________________________________________________________________
echo Install external dependencies using pip:
verbose_eval ${BIN}/python ${BIN}/pip install --verbose --log=pip.log --requirement requirements/external_apps.txt

echo _____________________________________________________________________
echo add a manage.sh script:
verbose_eval ln ${PYLUCID_ENV}/src/pylucid/scripts/manage.sh ${PYLUCID_ENV}/
verbose_eval chmod +x ${PYLUCID_ENV}/manage.sh

echo =====================================================================
echo
echo virtual PyLucid environment ready.
echo You can make this:
echo
echo Go into virtual environment:
echo   cd ${PYLUCID_ENV}
echo
echo create tables:
echo   ./manage.sh syncdb
echo
echo startup dev server:
echo   ./manage.sh runserver
echo