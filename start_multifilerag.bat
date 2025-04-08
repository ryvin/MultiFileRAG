@echo off
echo Setting up MultiFileRAG...

REM Check if conda is installed
where conda >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Conda is not installed or not in PATH.
    echo Please install conda before continuing.
    echo Visit https://docs.conda.io/en/latest/miniconda.html for installation instructions.
    pause
    exit /b 1
)

REM Check if the environment exists
conda env list | findstr /C:"multifilerag" >nul
if %ERRORLEVEL% NEQ 0 (
    echo Creating conda environment...
    conda env create -f environment.yml
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create conda environment.
        pause
        exit /b 1
    )
)

REM Activate the environment and start the server
echo Starting MultiFileRAG server...
call conda activate multifilerag
python start_server.py --auto-scan

pause
