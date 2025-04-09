@echo off
echo Checking MultiFileRAG database services status...
C:\Users\raul\.conda\envs\multifilerag\python.exe manage_databases.py status
pause
