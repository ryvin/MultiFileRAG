@echo off
echo Starting MultiFileRAG server...

REM Check if conda is available
if exist "C:\ProgramData\anaconda3\Scripts\activate.bat" (
    echo Activating multifilerag environment...
    call "C:\ProgramData\anaconda3\Scripts\activate.bat" multifilerag
) else if exist "C:\Users\raul\.conda\envs\multifilerag" (
    echo Activating multifilerag environment...
    call "C:\Users\raul\.conda\Scripts\activate.bat" multifilerag
) else (
    echo Conda not found. Please make sure Anaconda or Miniconda is installed.
    goto :error
)

REM Check if Ollama is running
echo Checking if Ollama is running...
curl -s http://localhost:11434/api/version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Ollama server is not running. Please start Ollama before continuing.
    goto :error
)
echo Ollama server is running.

REM Create/verify directories
echo Creating/verifying directories...
if not exist "inputs" mkdir "inputs"
if not exist "rag_storage" mkdir "rag_storage"
echo Directories created/verified: ./inputs, ./rag_storage

REM Start the server
echo Starting MultiFileRAG server on 0.0.0.0:9621...
python multifilerag_server.py
if %ERRORLEVEL% neq 0 goto :error

goto :end

:error
echo Server startup failed. Please try the following manual steps:
echo 1. Open Anaconda Prompt
echo 2. Run: conda activate multifilerag
echo 3. Run: python multifilerag_server.py

:end
echo Press any key to exit...
pause > nul
