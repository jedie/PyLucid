#!/bin/bash

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
verbose_eval ${BIN}/python ${BIN}/pip install --requirement requirements/external_apps.txt