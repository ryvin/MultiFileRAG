# PowerShell script to start MultiFileRAG with PostgreSQL, Neo4j, Redis, and Node.js databases
Write-Host "Starting MultiFileRAG with database support..." -ForegroundColor Green

# Create required directories if they don't exist
if (-not (Test-Path "docker/postgres")) {
    New-Item -Path "docker/postgres" -ItemType Directory -Force | Out-Null
}
if (-not (Test-Path "docker/neo4j")) {
    New-Item -Path "docker/neo4j" -ItemType Directory -Force | Out-Null
}
if (-not (Test-Path "docker/nodejs")) {
    New-Item -Path "docker/nodejs" -ItemType Directory -Force | Out-Null
}

# Check if Docker is running
try {
    $dockerStatus = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Docker is running." -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed or not running. Please install Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Start the database containers
Write-Host "Starting database containers..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start database containers." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Database containers started successfully." -ForegroundColor Green

# Wait for PostgreSQL to be ready
Write-Host "Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
$retries = 0
$maxRetries = 30
$ready = $false

while (-not $ready -and $retries -lt $maxRetries) {
    try {
        $result = docker exec multifilerag-postgres pg_isready -U postgres 2>&1
        if ($LASTEXITCODE -eq 0) {
            $ready = $true
        } else {
            $retries++
            Start-Sleep -Seconds 1
        }
    } catch {
        $retries++
        Start-Sleep -Seconds 1
    }
}

if (-not $ready) {
    Write-Host "❌ PostgreSQL is not ready after $maxRetries attempts. Please check the container logs." -ForegroundColor Red
    exit 1
}
Write-Host "✅ PostgreSQL is ready." -ForegroundColor Green

# Wait for Neo4j to be ready
Write-Host "Waiting for Neo4j to be ready..." -ForegroundColor Yellow
$retries = 0
$maxRetries = 60  # Neo4j can take longer to start
$ready = $false

while (-not $ready -and $retries -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:7474" -Method GET -TimeoutSec 1 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $ready = $true
        } else {
            $retries++
            Start-Sleep -Seconds 1
        }
    } catch {
        $retries++
        Start-Sleep -Seconds 1
    }
}

if (-not $ready) {
    Write-Host "⚠️ Neo4j is not ready after $maxRetries attempts. Continuing anyway..." -ForegroundColor Yellow
} else {
    Write-Host "✅ Neo4j is ready." -ForegroundColor Green
}

# Wait for Redis to be ready
Write-Host "Waiting for Redis to be ready..." -ForegroundColor Yellow
$retries = 0
$maxRetries = 30
$ready = $false

while (-not $ready -and $retries -lt $maxRetries) {
    try {
        $result = docker exec multifilerag-redis redis-cli ping 2>&1
        if ($result -eq "PONG") {
            $ready = $true
        } else {
            $retries++
            Start-Sleep -Seconds 1
        }
    } catch {
        $retries++
        Start-Sleep -Seconds 1
    }
}

if (-not $ready) {
    Write-Host "⚠️ Redis is not ready after $maxRetries attempts. Continuing anyway..." -ForegroundColor Yellow
} else {
    Write-Host "✅ Redis is ready." -ForegroundColor Green
}

# Wait for Node.js to be ready
Write-Host "Waiting for Node.js API to be ready..." -ForegroundColor Yellow
$retries = 0
$maxRetries = 30
$ready = $false

while (-not $ready -and $retries -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -TimeoutSec 1 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $ready = $true
        } else {
            $retries++
            Start-Sleep -Seconds 1
        }
    } catch {
        $retries++
        Start-Sleep -Seconds 1
    }
}

if (-not $ready) {
    Write-Host "⚠️ Node.js API is not ready after $maxRetries attempts. Continuing anyway..." -ForegroundColor Yellow
} else {
    Write-Host "✅ Node.js API is ready." -ForegroundColor Green
}

# Start the MultiFileRAG server
Write-Host "Starting MultiFileRAG server..." -ForegroundColor Yellow
try {
    # Try to use conda-init and Enter-CondaEnvironment (PowerShell-specific commands)
    if (Get-Command "conda-init" -ErrorAction SilentlyContinue) {
        Write-Host "Initializing conda for PowerShell..." -ForegroundColor Yellow
        conda-init
    } elseif (Test-Path "C:\ProgramData\anaconda3\shell\condabin\conda-hook.ps1") {
        Write-Host "Loading conda hook..." -ForegroundColor Yellow
        & "C:\ProgramData\anaconda3\shell\condabin\conda-hook.ps1"
    } else {
        Write-Host "Conda not found. Using system Python." -ForegroundColor Yellow
    }

    # Try to activate the environment
    if (Get-Command "conda-activate" -ErrorAction SilentlyContinue) {
        conda-activate multifilerag
    } elseif (Get-Command "Enter-CondaEnvironment" -ErrorAction SilentlyContinue) {
        Enter-CondaEnvironment multifilerag
    } else {
        # Fall back to direct conda command
        & conda activate multifilerag
    }

    # Start the server
    python multifilerag_server.py
} catch {
    Write-Host "❌ Failed to start MultiFileRAG server: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Press Enter to exit..." -ForegroundColor Cyan
Read-Host
