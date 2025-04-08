@echo off
echo Installing PDF processing dependencies for MultiFileRAG in conda environment...

REM Check if conda is initialized in PowerShell
powershell -Command "if (-not (Get-Command conda -ErrorAction SilentlyContinue)) { Write-Host 'Conda not initialized in PowerShell. Initializing...' -ForegroundColor Yellow; & 'C:\ProgramData\anaconda3\shell\condabin\conda-hook.ps1'; conda-init }"

REM Activate the conda environment and install dependencies
powershell -Command "& 'C:\ProgramData\anaconda3\shell\condabin\conda-hook.ps1'; conda activate multifilerag; if ($?) { python install_pdf_conda_deps.py } else { Write-Host 'Failed to activate conda environment. Please activate it manually with: conda activate multifilerag' -ForegroundColor Red }"

echo.
echo If the installation was not successful, please try the following manual steps:
echo 1. Open Anaconda Prompt
echo 2. Run: conda activate multifilerag
echo 3. Run: pip install PyPDF2 unstructured[pdf] pdfplumber
echo.
pause
