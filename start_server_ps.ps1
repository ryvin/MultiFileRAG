# PowerShell script to start the MultiFileRAG server
Write-Host "Starting MultiFileRAG server..." -ForegroundColor Green

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

    # Check if Ollama is running
    Write-Host "Checking if Ollama is running..." -ForegroundColor Cyan
    $ollamaStatus = Invoke-RestMethod -Uri "http://localhost:11434/api/version" -Method Get -ErrorAction SilentlyContinue
    
    if ($ollamaStatus) {
        Write-Host "✅ Ollama server is running. Version: $($ollamaStatus.version)" -ForegroundColor Green
    } else {
        Write-Host "❌ Ollama server is not running. Please start Ollama before continuing." -ForegroundColor Red
        exit 1
    }
    
    # Create/verify directories
    Write-Host "Creating/verifying directories..." -ForegroundColor Cyan
    if (-not (Test-Path "E:/Code/MultiFileRAG/inputs")) {
        New-Item -Path "E:/Code/MultiFileRAG/inputs" -ItemType Directory | Out-Null
    }
    if (-not (Test-Path "E:/Code/MultiFileRAG/rag_storage")) {
        New-Item -Path "E:/Code/MultiFileRAG/rag_storage" -ItemType Directory | Out-Null
    }
    Write-Host "✅ Directories created/verified: ./inputs, ./rag_storage" -ForegroundColor Green
    
    # Start the server
    Write-Host "Starting MultiFileRAG server on 0.0.0.0:9621..." -ForegroundColor Cyan
    python "E:/Code/MultiFileRAG/multifilerag_server.py"
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "Server startup failed. Please try the following manual steps:" -ForegroundColor Yellow
    Write-Host "1. Open Anaconda PowerShell Prompt" -ForegroundColor Yellow
    Write-Host "2. Run: conda activate multifilerag" -ForegroundColor Yellow
    Write-Host "3. Run: python multifilerag_server.py" -ForegroundColor Yellow
}

Write-Host "Press Enter to exit..." -ForegroundColor Cyan
Read-Host
