@echo off
echo Stopping MultiFileRAG server...
taskkill /f /im python.exe /fi "WINDOWTITLE eq MultiFileRAG Server"

echo Starting MultiFileRAG server with new settings...
start "MultiFileRAG Server" C:\Users\raul\.conda\envs\multifilerag\python.exe multifilerag_server.py

echo Server restarted. The web UI is available at http://localhost:9621
