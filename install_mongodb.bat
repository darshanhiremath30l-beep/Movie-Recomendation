@echo off
echo Installing MongoDB Community Edition...
echo.

REM Check if MongoDB is already installed
where mongod >nul 2>&1
if %errorlevel% equ 0 (
    echo MongoDB is already installed.
    goto :start_mongo
)

REM Download MongoDB MSI installer
echo Downloading MongoDB Community Edition...
powershell -Command "& {Invoke-WebRequest -Uri 'https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-7.0.5-signed.msi' -OutFile 'mongodb-installer.msi'}"
if %errorlevel% neq 0 (
    echo Failed to download MongoDB. Please download manually from:
    echo https://www.mongodb.com/try/download/community
    pause
    exit /b 1
)

REM Install MongoDB silently
echo Installing MongoDB...
msiexec /i mongodb-installer.msi /quiet /norestart ADDLOCAL="Server,Client,Router,Miscellaneous" INSTALLLOCATION="C:\Program Files\MongoDB\Server\7.0"
if %errorlevel% neq 0 (
    echo Failed to install MongoDB. Please install manually.
    pause
    exit /b 1
)

REM Create data directory
echo Creating MongoDB data directory...
if not exist "C:\data\db" mkdir "C:\data\db"

REM Clean up installer
del mongodb-installer.msi

:start_mongo
REM Start MongoDB service
echo Starting MongoDB service...
net start MongoDB
if %errorlevel% neq 0 (
    echo Failed to start MongoDB service. Trying to start manually...
    start "MongoDB" "C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe" --dbpath "C:\data\db"
    timeout /t 3 /nobreak > nul
)

REM Verify MongoDB is running
echo Verifying MongoDB connection...
timeout /t 2 /nobreak > nul
"C:\Program Files\MongoDB\Server\7.0\bin\mongo.exe" --eval "db.stats()" >nul 2>&1
if %errorlevel% equ 0 (
    echo MongoDB is running successfully!
) else (
    echo MongoDB may not be running properly. Please check manually.
)

echo.
pause