@echo off
echo Reprocessing account statements with enhanced PDF processing...

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

REM Process all account statement PDFs
echo Processing account statements...

REM Count PDF files
set count=0
for %%f in (inputs\*Account Statements*.pdf) do set /a count+=1
echo Found %count% account statement PDFs to process.

REM Process each PDF file
for %%f in (inputs\*Account Statements*.pdf) do (
    echo Processing: %%~nxf
    python test_pdf_processing.py "%%~ff"
    timeout /t 2 /nobreak > nul
)

echo All account statements processed!
echo You can now restart the MultiFileRAG server and query your account statements.
goto :end

:error
echo Processing failed. Please make sure you've installed the required dependencies:
echo 1. Run install_pdf_dependencies.bat
echo 2. Try running this script again

:end
echo Press any key to exit...
pause > nul
