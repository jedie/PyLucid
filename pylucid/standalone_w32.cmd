@echo off

REM go into the same directory where this file stored (Project root)
cd /d "%~dp0"

REM use the local django packages
set PYTHONPATH="%~dp0"

:loop
    echo.
    echo Starting django development server...
    echo.

    python manage.py runserver
goto loop

pause