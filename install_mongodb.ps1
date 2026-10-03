# MongoDB Installation Script
Write-Host "Installing MongoDB Community Edition..." -ForegroundColor Green

# Check if MongoDB is already installed
$mongoPath = "C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe"
if (Test-Path $mongoPath) {
    Write-Host "MongoDB is already installed." -ForegroundColor Yellow
} else {
    # Download MongoDB
    Write-Host "Downloading MongoDB Community Edition..."
    $url = "https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-7.0.5-signed.msi"
    $output = "$PSScriptRoot\mongodb-installer.msi"

    try {
        Invoke-WebRequest -Uri $url -OutFile $output
        Write-Host "Download completed." -ForegroundColor Green
    } catch {
        Write-Host "Failed to download MongoDB. Please download manually from: $url" -ForegroundColor Red
        exit 1
    }

    # Install MongoDB
    Write-Host "Installing MongoDB..."
    $installArgs = "/i `"$output`" /quiet /norestart ADDLOCAL=`"Server,Client,Router,Miscellaneous`" INSTALLLOCATION=`"C:\Program Files\MongoDB\Server\7.0`""
    Start-Process -FilePath "msiexec.exe" -ArgumentList $installArgs -Wait

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install MongoDB. Please install manually." -ForegroundColor Red
        exit 1
    }

    # Clean up installer
    Remove-Item $output -Force
    Write-Host "MongoDB installed successfully." -ForegroundColor Green
}

# Create data directory
$dataDir = "C:\data\db"
if (!(Test-Path $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir -Force
    Write-Host "Created MongoDB data directory: $dataDir" -ForegroundColor Green
}

# Try to start MongoDB service
Write-Host "Starting MongoDB service..."
try {
    Start-Service -Name "MongoDB" -ErrorAction Stop
    Write-Host "MongoDB service started successfully." -ForegroundColor Green
} catch {
    Write-Host "Failed to start MongoDB service. Trying to start manually..." -ForegroundColor Yellow
    try {
        Start-Process -FilePath $mongoPath -ArgumentList "--dbpath", "`"$dataDir`"" -NoNewWindow
        Start-Sleep -Seconds 3
        Write-Host "MongoDB started manually." -ForegroundColor Green
    } catch {
        Write-Host "Failed to start MongoDB manually." -ForegroundColor Red
    }
}

# Verify connection
Write-Host "Verifying MongoDB connection..."
try {
    & "C:\Program Files\MongoDB\Server\7.0\bin\mongo.exe" --eval "db.stats()" | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "MongoDB is running successfully!" -ForegroundColor Green
    } else {
        Write-Host "MongoDB connection verification failed." -ForegroundColor Yellow
    }
} catch {
    Write-Host "MongoDB verification failed." -ForegroundColor Yellow
}

Write-Host "`nMongoDB installation completed." -ForegroundColor Green
Read-Host "Press Enter to continue"