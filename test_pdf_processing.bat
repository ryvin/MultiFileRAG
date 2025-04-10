@echo off
echo Testing PDF processing with enhanced capabilities...

REM Define the PDF file to test
set pdfFile=E:\Code\MultiFileRAG\inputs\1978897 Account Statements_2024-08-31.pdf

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

REM Run the test script
echo Running PDF processing test on: %pdfFile%
python test_pdf_processing.py "%pdfFile%"
if %ERRORLEVEL% neq 0 goto :error

echo Test complete!
goto :end

:error
echo Test failed. Please make sure you've installed the required dependencies:
echo 1. Run install_pdf_dependencies.bat
echo 2. Try running this test again

:end
echo Press any key to exit...
pause > nul
