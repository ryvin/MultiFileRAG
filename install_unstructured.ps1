# PowerShell script to install unstructured library for PDF processing
Write-Host "Installing unstructured library for PDF processing..." -ForegroundColor Green

# Check if conda is available
try {
    # Try to use conda-init and Enter-CondaEnvironment (PowerShell-specific commands)
    if (Get-Command "conda-init" -ErrorAction SilentlyContinue) {
        Write-Host "Initializing conda for PowerShell..." -ForegroundColor Yellow
        conda-init
    } elseif (Test-Path "C:\ProgramData\anaconda3\shell\condabin\conda-hook.ps1") {
        Write-Host "Loading conda hook..." -ForegroundColor Yellow
        & "C:\ProgramData\anaconda3\shell\condabin\conda-hook.ps1"
    } else {
        Write-Host "Conda not found. Please make sure Anaconda or Miniconda is installed." -ForegroundColor Red
        exit 1
    }

    # Try to activate the environment
    Write-Host "Activating multifilerag environment..." -ForegroundColor Yellow
    if (Get-Command "conda-activate" -ErrorAction SilentlyContinue) {
        conda-activate multifilerag
    } elseif (Get-Command "Enter-CondaEnvironment" -ErrorAction SilentlyContinue) {
        Enter-CondaEnvironment multifilerag
    } else {
        # Fall back to direct conda command
        & conda activate multifilerag
    }

    # Install unstructured with PDF support
    Write-Host "Installing unstructured with PDF support..." -ForegroundColor Cyan
    pip install "unstructured[pdf]"
    
    Write-Host "Installation complete!" -ForegroundColor Green
    Write-Host "You can now process PDFs with the unstructured library." -ForegroundColor Green
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "Installation failed. Please try the following manual steps:" -ForegroundColor Yellow
    Write-Host "1. Open Anaconda PowerShell Prompt" -ForegroundColor Yellow
    Write-Host "2. Run: conda activate multifilerag" -ForegroundColor Yellow
    Write-Host "3. Run: pip install 'unstructured[pdf]'" -ForegroundColor Yellow
}

Write-Host "Press Enter to exit..." -ForegroundColor Cyan
Read-Host
