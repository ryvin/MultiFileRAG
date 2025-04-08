# PowerShell script to test PDF processing with enhanced capabilities
Write-Host "Testing PDF processing with enhanced capabilities..." -ForegroundColor Green

# Define the PDF file to test
$pdfFile = "E:/Code/MultiFileRAG/inputs/1978897 Account Statements_2024-08-31.pdf"

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

    # Run the test script
    Write-Host "Running PDF processing test on: $pdfFile" -ForegroundColor Cyan
    python "E:/Code/MultiFileRAG/test_pdf_processing.py" "$pdfFile"
    
    Write-Host "Test complete!" -ForegroundColor Green
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "Test failed. Please make sure you've installed the required dependencies:" -ForegroundColor Yellow
    Write-Host "1. Run install_pdf_deps_ps.ps1" -ForegroundColor Yellow
    Write-Host "2. Try running this test again" -ForegroundColor Yellow
}

Write-Host "Press Enter to exit..." -ForegroundColor Cyan
Read-Host
