# PowerShell script to reprocess account statements with enhanced PDF processing
Write-Host "Reprocessing account statements with enhanced PDF processing..." -ForegroundColor Green

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

    # Process all account statement PDFs in the inputs directory
    Write-Host "Processing account statement PDFs..." -ForegroundColor Cyan
    
    # Get all account statement PDFs
    $pdfFiles = Get-ChildItem -Path "E:/Code/MultiFileRAG/inputs" -Filter "*Account Statements*.pdf"
    
    Write-Host "Found $($pdfFiles.Count) account statement PDFs to process." -ForegroundColor Cyan
    
    foreach ($pdf in $pdfFiles) {
        Write-Host "Processing: $($pdf.Name)" -ForegroundColor Yellow
        
        # Extract text using our enhanced PDF processing
        python "E:/Code/MultiFileRAG/test_pdf_processing.py" "$($pdf.FullName)"
        
        # Wait a moment before processing the next file
        Start-Sleep -Seconds 2
    }
    
    Write-Host "All account statements processed!" -ForegroundColor Green
    Write-Host "You can now restart the MultiFileRAG server and query your account statements." -ForegroundColor Green
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "Processing failed. Please make sure you've installed the required dependencies:" -ForegroundColor Yellow
    Write-Host "1. Run install_pdf_deps_ps.ps1" -ForegroundColor Yellow
    Write-Host "2. Try running this script again" -ForegroundColor Yellow
}

Write-Host "Press Enter to exit..." -ForegroundColor Cyan
Read-Host
