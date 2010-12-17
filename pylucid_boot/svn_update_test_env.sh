#!/bin/bash

function verbose_eval {
    echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    echo ${PWD}\$ $*
    echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    eval $*
    echo ---------------------------------------------------------------------
    echo
}

BASE_DIR=${PWD%/*}
echo "use base dir: ${BASE_DIR}"
cd ${BASE_DIR}

PYLUCID_ENV=PyLucid_env

echo _____________________________________________________________________
echo Update via SVN:

verbose_eval svn update ${PYLUCID_ENV}/src/pylucid
verbose_eval svn update ${PYLUCID_ENV}/src/django
verbose_eval svn update ${PYLUCID_ENV}/src/dbpreferences
verbose_eval svn update ${PYLUCID_ENV}/src/django-tools
verbose_eval svn update ${PYLUCID_ENV}/src/reversion
verbose_eval svn update ${PYLUCID_ENV}/src/tagging

echo =====================================================================
echo
echo virtual PyLucid environment updated
