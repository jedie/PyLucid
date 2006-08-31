#!/bin/sh

# Startet einen lokalen Test-Server.

while :
do
    echo 'Starte Webserver...'

    # für Python 2.4:
    python PyLucid_app.py

    # für Python <2.4:
    # python PyLucid_app_withBackports.py

    echo ''
    echo 'restart des Servers mit ENTER...'
    read
done

echo 'ENTER zum Beenden.'
read