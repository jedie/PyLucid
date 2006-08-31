@echo off

REM Startet einen lokalen Test-Server.

REM Evtl. muß der Pfad zur python.exe angepasst werden, wenn
REM der Python-Interpreter nicht im Pfad ist!

:loop
    echo Starte Webserver...

    REM für Python 2.4:
    python PyLucid_app.py

    REM für Python <2.4:
    REM python PyLucid_app_withBackports.py

    echo.
    echo Restart des Server:
    pause
goto loop

pause