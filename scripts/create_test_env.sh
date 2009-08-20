#!/bin/bash

# pip
# ${BIN}/python ${BIN}/pip install --help

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
echo ${BASE_DIR}

cd ${BASE_DIR}

PYLUCID_ENV=PyLucid_env
BIN=${PYLUCID_ENV}/bin
PIP_LOG=${PYLUCID_ENV}/pip.log
EXT_APPS_TXT=scripts/requirements/external_apps.txt

if python scripts/pre_check.py;
then
    echo "requirements pre test ok"
else
    echo "requirements pre test failed!"
    echo " *** Please install requirements first and start this script again!"
    exit
fi

# This script created by create_bootstrap_script.py
BOOTSTRAP_SCRIPT=scripts/pylucid-boot.py

echo _____________________________________________________________________
echo Create virtual environment:
verbose_eval python ${BOOTSTRAP_SCRIPT} ${PYLUCID_ENV}

echo _____________________________________________________________________
echo activate the virtual environment:
verbose_eval source ${BIN}/activate

echo _____________________________________________________________________
echo Install external dependencies using pip:
verbose_eval ${BIN}/python ${BIN}/pip install --verbose --log=${PIP_LOG} --requirement ${EXT_APPS_TXT}

if [ -f ${PYLUCID_ENV}/src/pylucid/scripts/manage.sh ]
  then
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
    echo   cd ../${PYLUCID_ENV}/
    echo
    echo create tables:
    echo   ./manage.sh syncdb
    echo
    echo startup dev server:
    echo   ./manage.sh runserver
    echo
  else
    echo "Seems, something works wrong?!?"
fi

