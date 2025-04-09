@echo off
echo Updating MultiFileRAG conda environment with all dependencies from requirements.txt...

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

REM Update the environment with all dependencies from requirements.txt
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 goto :error

echo Environment update complete!
echo You can now process problematic PDFs with the enhanced PDF processing capabilities.
goto :end

:error
echo Environment update failed. Please try the following manual steps:
echo 1. Open Anaconda Prompt
echo 2. Run: conda activate multifilerag
echo 3. Run: pip install -r requirements.txt

:end
echo Press any key to exit...
pause > nul
