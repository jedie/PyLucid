@echo off

REM go into the same directory where this file stored (Project root)
cd /d "%~dp0"

if not exist "%~dp0PyLucid\settings.py" (
    echo.
    echo Error: There exist no settings.py!
    echo.
    echo Please create "%~dp0PyLucid\settings.py"
    echo.
    echo More info at http://www.pylucid.org
    echo.
    pause
    exit
)

REM use the local django packages
set PYTHONPATH="%~dp0"

echo.
echo Starting django development server...
echo.

python manage.py runserver

pause