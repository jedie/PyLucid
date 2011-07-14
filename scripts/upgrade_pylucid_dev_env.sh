#!/bin/bash

# symlink or copy this file into: /home/FooBar/PyLucid_env/

function verbose_eval {
    echo + $*
    eval $*
}

echo _____________________________________________________________________
echo activate the virtual environment:
verbose_eval source bin/activate

echo _____________________________________________________________________
echo upgrade virtual environment:
(
	set -x
	bin/python src/pylucid/scripts/upgrade_pylucid_env.py --env_type=developer
)