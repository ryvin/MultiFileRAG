@echo off
echo Stopping MultiFileRAG database services...
C:\Users\raul\.conda\envs\multifilerag\python.exe manage_databases.py stop
pause
