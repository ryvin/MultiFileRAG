@echo off
echo Installing PDF processing dependencies for MultiFileRAG...

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

REM Install the dependencies
echo Installing PyPDF2...
pip install PyPDF2
if %ERRORLEVEL% neq 0 goto :error

echo Installing unstructured with PDF support...
pip install "unstructured[pdf]"
if %ERRORLEVEL% neq 0 goto :error

echo Installing pdfplumber...
pip install pdfplumber
if %ERRORLEVEL% neq 0 goto :error

echo Installation complete!
echo You can now process problematic PDFs with the enhanced PDF processing capabilities.
goto :end

:error
echo Installation failed. Please try the following manual steps:
echo 1. Open Anaconda Prompt
echo 2. Run: conda activate multifilerag
echo 3. Run: pip install PyPDF2 "unstructured[pdf]" pdfplumber

:end
echo Press any key to exit...
pause > nul
