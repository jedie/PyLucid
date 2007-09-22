@echo off

REM go into the same directory where this file stored (Project root)
cd /d "%~dp0"
set PYTHONPATH="%~dp0"
xcopy django\bin\django-admin.py .\ /d /y

:loop
    echo Starting django development server...

    python django-admin.py runserver --settings=PyLucid.settings

    echo.
    echo Restart des Server:
    pause
goto loop

del django-admin.py

pause