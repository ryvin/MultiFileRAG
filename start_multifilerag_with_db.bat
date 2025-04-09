@echo off
echo Starting MultiFileRAG with database support...

REM Create required directories if they don't exist
if not exist "docker\postgres" mkdir "docker\postgres"
if not exist "docker\neo4j" mkdir "docker\neo4j"
if not exist "docker\nodejs" mkdir "docker\nodejs"

REM Check if Docker is running
docker info > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [31m❌ Docker is not running. Please start Docker Desktop and try again.[0m
    goto :error
)
echo [32m✅ Docker is running.[0m

REM Start the database containers
echo [33mStarting database containers...[0m
docker-compose up -d
if %ERRORLEVEL% neq 0 (
    echo [31m❌ Failed to start database containers.[0m
    goto :error
)
echo [32m✅ Database containers started successfully.[0m

REM Wait for PostgreSQL to be ready
echo [33mWaiting for PostgreSQL to be ready...[0m
set retries=0
set maxRetries=30
set ready=false

:postgres_loop
if "%ready%"=="true" goto :postgres_done
if %retries% geq %maxRetries% goto :postgres_timeout
docker exec multifilerag-postgres pg_isready -U postgres > nul 2>&1
if %ERRORLEVEL% equ 0 (
    set ready=true
) else (
    set /a retries+=1
    timeout /t 1 /nobreak > nul
    goto :postgres_loop
)

:postgres_timeout
if "%ready%"=="false" (
    echo [31m❌ PostgreSQL is not ready after %maxRetries% attempts. Please check the container logs.[0m
    goto :error
)

:postgres_done
echo [32m✅ PostgreSQL is ready.[0m

REM Wait for Neo4j to be ready
echo [33mWaiting for Neo4j to be ready...[0m
set retries=0
set maxRetries=60
set ready=false

:neo4j_loop
if "%ready%"=="true" goto :neo4j_done
if %retries% geq %maxRetries% goto :neo4j_timeout
curl -s -o nul -w "%%{http_code}" http://localhost:7474 > temp.txt 2>nul
set /p status=<temp.txt
del temp.txt
if "%status%"=="200" (
    set ready=true
) else (
    set /a retries+=1
    timeout /t 1 /nobreak > nul
    goto :neo4j_loop
)

:neo4j_timeout
if "%ready%"=="false" (
    echo [33m⚠️ Neo4j is not ready after %maxRetries% attempts. Continuing anyway...[0m
) else (
    :neo4j_done
    echo [32m✅ Neo4j is ready.[0m
)

REM Wait for Redis to be ready
echo [33mWaiting for Redis to be ready...[0m
set retries=0
set maxRetries=30
set ready=false

:redis_loop
if "%ready%"=="true" goto :redis_done
if %retries% geq %maxRetries% goto :redis_timeout
docker exec multifilerag-redis redis-cli ping > temp.txt 2>nul
set /p result=<temp.txt
del temp.txt
if "%result%"=="PONG" (
    set ready=true
) else (
    set /a retries+=1
    timeout /t 1 /nobreak > nul
    goto :redis_loop
)

:redis_timeout
if "%ready%"=="false" (
    echo [33m⚠️ Redis is not ready after %maxRetries% attempts. Continuing anyway...[0m
) else (
    :redis_done
    echo [32m✅ Redis is ready.[0m
)

REM Wait for Node.js to be ready
echo [33mWaiting for Node.js API to be ready...[0m
set retries=0
set maxRetries=30
set ready=false

:nodejs_loop
if "%ready%"=="true" goto :nodejs_done
if %retries% geq %maxRetries% goto :nodejs_timeout
curl -s -o nul -w "%%{http_code}" http://localhost:3000 > temp.txt 2>nul
set /p status=<temp.txt
del temp.txt
if "%status%"=="200" (
    set ready=true
) else (
    set /a retries+=1
    timeout /t 1 /nobreak > nul
    goto :nodejs_loop
)

:nodejs_timeout
if "%ready%"=="false" (
    echo [33m⚠️ Node.js API is not ready after %maxRetries% attempts. Continuing anyway...[0m
) else (
    :nodejs_done
    echo [32m✅ Node.js API is ready.[0m
)

REM Start the MultiFileRAG server
echo [33mStarting MultiFileRAG server...[0m

REM Activate conda environment
if exist "C:\ProgramData\anaconda3\Scripts\activate.bat" (
    echo Activating multifilerag environment...
    call "C:\ProgramData\anaconda3\Scripts\activate.bat" multifilerag
) else if exist "C:\Users\raul\.conda\envs\multifilerag" (
    echo Activating multifilerag environment...
    call "C:\Users\raul\.conda\Scripts\activate.bat" multifilerag
) else (
    echo [33mConda not found. Using system Python.[0m
)

REM Start the server
python multifilerag_server.py
if %ERRORLEVEL% neq 0 (
    echo [31m❌ Failed to start MultiFileRAG server.[0m
    goto :error
)

goto :end

:error
echo [31mAn error occurred during startup.[0m
pause
exit /b 1

:end
echo Press any key to exit...
pause > nul
