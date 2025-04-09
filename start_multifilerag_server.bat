@echo off
echo Starting MultiFileRAG server with database support...

REM Check if the --no-db-autostart flag was passed
set NO_DB_AUTOSTART=
if "%1"=="--no-db-autostart" set NO_DB_AUTOSTART=--no-db-autostart

REM Install required packages if needed
echo Checking for required packages...
C:\Users\raul\.conda\envs\multifilerag\python.exe -m pip install redis requests

REM Start the server with auto-scan and database auto-start (unless disabled)
C:\Users\raul\.conda\envs\multifilerag\python.exe multifilerag_server.py --auto-scan %NO_DB_AUTOSTART%
