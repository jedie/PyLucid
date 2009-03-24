#!/bin/bash

function verbose_eval {
    echo ---------------------------------------------------------------------
    echo $*
    echo ---------------------------------------------------------------------
    eval $*
}

verbose_eval svn checkout http://code.djangoproject.com/svn/django/trunk/django/