#!/bin/bash

function verbose_eval {
    echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    echo $*
    echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    eval $*
    echo ---------------------------------------------------------------------
    echo
}

PYLUCID_ENV=../PyLucid_env
BIN=${PYLUCID_ENV}/bin

#${BIN}/python ${BIN}/pip install --help

echo _____________________________________________________________________
echo activate the virtual environment:
verbose_eval source ${BIN}/activate

echo _____________________________________________________________________
echo Install external dependencies using pip:
verbose_eval ${BIN}/python ${BIN}/pip install --upgrade --verbose --log=pip_update.log --requirement requirements/external_apps.txt

echo _____________________________________________________________________
echo add a manage.sh script:
verbose_eval ln ${PYLUCID_ENV}/src/pylucid/scripts/manage.sh ${PYLUCID_ENV}/
verbose_eval chmod +x ${PYLUCID_ENV}/manage.sh

echo =====================================================================
echo
echo virtual PyLucid environment updated
