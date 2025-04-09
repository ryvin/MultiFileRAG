@echo off
echo Stopping MultiFileRAG database containers...

REM Stop the database containers
docker-compose down
if %ERRORLEVEL% neq 0 (
    echo Failed to stop database containers.
    goto :error
)
echo Database containers stopped successfully.

goto :end

:error
echo An error occurred while stopping the database containers.
exit /b 1

:end
echo Press any key to exit...
pause > nul
