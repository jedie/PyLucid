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

echo
echo "---------------------------------------------------------------------"
echo "Create PyLucid virtual environemten here:"
echo
echo ${BASE_DIR}
echo
echo "Important:"
echo "You can't move a environment into a other directory, after creating them!"
echo "see: http://pypi.python.org/pypi/virtualenv#making-environments-relocatable"
echo
echo "Continue? [Y/n]"
read -n 1 CHOICE
echo
if [ "$CHOICE" != "y" -a "$CHOICE" != "Y" -a "$CHOICE" != "j" -a "$CHOICE" != "J" ]
then
    echo "abort"
    exit
fi

cd ${BASE_DIR}

BIN=${BASE_DIR}/bin
PIP_LOG=${BASE_DIR}/pip.log
EXT_APPS_TXT=scripts/requirements/external_apps.txt
# This script created by create_bootstrap_script.py
BOOTSTRAP_SCRIPT=scripts/pylucid-boot.py

echo
echo "---------------------------------------------------------------------"
if python scripts/pre_check.py;
then
    echo "requirements pre test ok"
else
    echo "requirements pre test failed!"
    echo " *** Please install requirements first and start this script again!"
    exit
fi



echo
echo "---------------------------------------------------------------------"
echo "Please select how the pylucid own projects should be checkout:"
echo
echo "(1) Python packages from PyPi" 
echo "(1) source via SVN only (checkout git repository via github svn gateway)"
echo "(2) source via git and clone with readonly"
echo "(3) source via git and clone writeable (Needs github pubkey auth!)"
echo
echo "(abort with Strg-C)"
echo
echo "Please select: [1,2,3] (default: 1)"
read -n 1 CHOICE
echo

case $CHOICE in
    1)  REQUIREMENTS=scripts/requirements/own_projects_pypi.txt
        ;;
    2)  REQUIREMENTS=scripts/requirements/own_projects_svn.txt
        ;;
    3)  REQUIREMENTS=scripts/requirements/own_projects_git_readonly.txt
        ;;
    4)  REQUIREMENTS=scripts/requirements/own_projects_git_writeable.txt
        ;;
    *)  echo "Wrong choice, abort..."
        exit
        ;;
esac



echo _____________________________________________________________________
echo Create virtual environment:
verbose_eval python ${BOOTSTRAP_SCRIPT} ${BASE_DIR}

echo _____________________________________________________________________
echo activate the virtual environment:
verbose_eval source ${BIN}/activate

echo _____________________________________________________________________
echo Install external dependencies using pip:
verbose_eval ${BIN}/python ${BIN}/pip install --verbose --log=${PIP_LOG} --requirement ${REQUIREMENTS}

if [ -f ${BASE_DIR}/src/pylucid/scripts/manage.sh ]
  then
    echo _____________________________________________________________________
    echo add a manage.sh script:
    verbose_eval ln ${BASE_DIR}/src/pylucid/scripts/manage.sh ${BASE_DIR}/
    verbose_eval chmod +x ${BASE_DIR}/manage.sh

    echo =====================================================================
    echo
    echo virtual PyLucid environment ready.
    echo You can make this:
    echo
    echo Go into virtual environment:
    echo   cd ${BASE_DIR}
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

