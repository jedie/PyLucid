#!/bin/sh

# use the local django packages
export PYTHONPATH=${PWD}

echo ''
echo 'Starting django development server...'
echo ''

python manage.py runserver $*