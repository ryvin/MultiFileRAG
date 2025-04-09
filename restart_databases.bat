@echo off
echo Restarting MultiFileRAG database services...
C:\Users\raul\.conda\envs\multifilerag\python.exe manage_databases.py restart
pause
