#!/bin/sh

# use the local django packages
export PYTHONPATH=${PWD}

while :
do
    echo ''
    echo 'Starting django development server...'
    echo ''

    python manage.py runserver $*
done