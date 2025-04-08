@echo off
echo Testing PDF processing with enhanced capabilities...

REM Check if conda is initialized in PowerShell
powershell -Command "if (-not (Get-Command conda -ErrorAction SilentlyContinue)) { Write-Host 'Conda not initialized in PowerShell. Initializing...' -ForegroundColor Yellow; & 'C:\ProgramData\anaconda3\shell\condabin\conda-hook.ps1'; conda-init }"

REM Activate the conda environment and run the test script
powershell -Command "& 'C:\ProgramData\anaconda3\shell\condabin\conda-hook.ps1'; conda activate multifilerag; if ($?) { python test_pdf_processing.py 'E:/Code/MultiFileRAG/inputs/1978897 Account Statements_2024-08-31.pdf' } else { Write-Host 'Failed to activate conda environment. Please activate it manually with: conda activate multifilerag' -ForegroundColor Red }"

echo.
echo If the test was not successful, please make sure you've installed the required dependencies:
echo 1. Run install_pdf_conda_deps.bat
echo 2. Try running this test again
echo.
pause
