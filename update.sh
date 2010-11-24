#!/bin/bash

if [ -e .git ];
then
    (
        set -x
        git pull origin master
    )
elif [ -e .svn ];
then
    (
        set -x
        svn update
    )
else
    echo "no .git or .svn directory found. Can't update"
fi