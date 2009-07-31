#!/bin/bash

function verbose_eval {
    echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    echo PWD: ${PWD}
    echo $*
    echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    eval $*
    echo ---------------------------------------------------------------------
    echo
}

BASE_DIR=${PWD%/*}
echo "use base dir: ${BASE_DIR}"
cd ${BASE_DIR}

PYLUCID_ENV=PyLucid_env
BIN=${PYLUCID_ENV}/bin
PIP_LOG=${PYLUCID_ENV}/pip_update.log
EXT_APPS_TXT=scripts/requirements/external_apps.txt

#${BIN}/python ${BIN}/pip install --help

echo _____________________________________________________________________
echo activate the virtual environment:
verbose_eval source ${BIN}/activate

echo _____________________________________________________________________
echo Install external dependencies using pip:
verbose_eval ${BIN}/python ${BIN}/pip install --upgrade --verbose --log=${PIP_LOG} --requirement ${EXT_APPS_TXT}

echo =====================================================================
echo
echo virtual PyLucid environment updated
