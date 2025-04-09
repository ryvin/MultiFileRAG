@echo off
echo Installing unstructured library for PDF processing...

REM Check if conda is available
if exist "C:\ProgramData\anaconda3\Scripts\activate.bat" (
    echo Activating multifilerag environment...
    call "C:\ProgramData\anaconda3\Scripts\activate.bat" multifilerag
) else if exist "C:\Users\raul\.conda\envs\multifilerag" (
    echo Activating multifilerag environment...
    call "C:\Users\raul\.conda\Scripts\activate.bat" multifilerag
) else (
    echo Conda environment not found. Please make sure Anaconda or Miniconda is installed.
    echo and the multifilerag environment exists.
    goto :error
)

REM Install unstructured with PDF support
echo Installing unstructured with PDF support...
pip install "unstructured[pdf]"
if %ERRORLEVEL% neq 0 goto :error

echo Installation complete!
echo You can now process PDFs with the unstructured library.
goto :end

:error
echo Installation failed. Please try the following manual steps:
echo 1. Open Anaconda Prompt
echo 2. Run: conda activate multifilerag
echo 3. Run: pip install "unstructured[pdf]"

:end
echo Press any key to exit...
pause > nul
