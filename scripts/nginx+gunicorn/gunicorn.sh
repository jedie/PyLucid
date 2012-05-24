#!/bin/bash


# -----------------------------------------------------------------------------
#   gunicorn.sh
#   ~~~~~~~~~~~
#
#   Script to control gunicorn for start, stop, reload etc.
#   The server will communicate via '/tmp/gunicorn.sock'. This path must
#   be the same as in nginx.conf
#
#   Usage:
#       $ ./gunicorn.sh {start|stop|restart|reload|status}
#
#   You should change some path in this script, see below!
#
#   After startup you can check if the sock exist with, e.g.:
#       netstat --protocol=unix -nlp
#
#   Important:
#   The gunicorn server process would inherit the user who starts this script!
#   use sudo e.g.:
#       $ sudo -u www ./gunicorn.sh start
#
#    :copyleft: 2012 by the PyLucid team, see AUTHORS for more details.
#    :license: GNU GPL v3 or above, see LICENSE for more details.
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# *** change these paths ***
VIRTUAL_ACTIVATE=~/PyLucid_env/bin/activate
PAGE_INSTANCE=/var/www/YourSite/
# -----------------------------------------------------------------------------

LOG_FILE=/var/log/gunicorn.log
PID_FILE=/var/run/gunicorn.pid
SOCK=/tmp/gunicorn.sock
CALL_INFO="$0 $*"


if [ $(whoami) == 'root' ]; then
    info "Error: Don't run this script as 'root' !"
    exit 1
fi


function verbose_eval {
    echo "--------------------------------------------------------------------"
    echo $*
    echo "--------------------------------------------------------------------"
    eval $*
}


function tail_log {
    sleep 0.5
    (
        set -x
        tail ${LOG_FILE}
    )
}


function do_start {
    logger start gunicorn by ${CALL_INFO}
    verbose_eval source ${VIRTUAL_ACTIVATE}
    (
        cd ${PAGE_INSTANCE}
        gunicorn --workers=3 wsgi_app:wsgi_handler --bind unix:${SOCK} --log-file=${LOG_FILE} --pid=${PID_FILE} --daemon
    )
    echo "gunicorn start..."
    tail_log
}


function do_stop {
    logger stop gunicorn by ${CALL_INFO}
    if [ -f ${PID_FILE} ]; then
        PID=`cat ${PID_FILE}`
        rm ${PID_FILE}
        (
            set -x
            kill -15 $PID
        )
        sleep 1
    else
        echo "PID file '${PID_FILE}' not exists."
    fi
    (
        set -x
        killall -v gunicorn
    )
    echo "gunicorn stopped..."
    tail_log
}


function do_reload {
    logger reload gunicorn by ${CALL_INFO}
    if [ -f ${PID_FILE} ]; then
        PID=`cat ${PID_FILE}`
        (
            set -x
            kill -HUP $PID
        )
    else
        echo "Error: PID file '${PID_FILE}' not exists!"
        (
            set -x
            killall --signal HUP gunicorn -v
        )
    fi
    echo "gunicorn reload..."
    tail_log
}


function do_status {
    echo call info: ${CALL_INFO}
    (
        set -x
        netstat --protocol=unix -nlp | grep python
        tail ${LOG_FILE}
    )
}


case "$1" in
    start)
        do_start
        ;;
    stop)
        do_stop
        ;;
    status)
        do_status
        ;;
    restart)
        do_stop
        do_start
        ;;
    reload)
        do_reload
        ;;
    *)
        echo $"Usage: $0 {start|stop|restart|reload|status}"
        exit 1
esac
