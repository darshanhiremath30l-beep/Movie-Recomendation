@echo off
echo Starting Movie Recommendation System...

REM Check if MongoDB is running
echo Checking MongoDB service...
net start | find "MongoDB" >nul 2>&1
if %errorlevel% neq 0 (
    REM Check if MongoDB binaries exist in common locations
    if exist "C:\Program Files\MongoDB\Server\*\bin\mongod.exe" (
        echo MongoDB found in C:\ drive.
        goto :check_mongo_connection
    ) else if exist "D:\Program Files\MongoDB\Server\*\bin\mongod.exe" (
        echo MongoDB found in D:\ drive.
        goto :check_mongo_connection
    ) else if exist "D:\MongoDB\Server\*\bin\mongod.exe" (
        echo MongoDB found in D:\MongoDB.
        goto :check_mongo_connection
    ) else (
        echo MongoDB service not found and binaries not located.
        echo.
        echo Choose an option:
        echo 1. Install MongoDB automatically (batch installer)
        echo 2. Install MongoDB automatically (PowerShell installer)
        echo 3. Setup existing MongoDB installation (enter custom path)
        echo 4. Continue with offline data (limited functionality)
        echo.
        set /p choice="Enter your choice (1, 2, 3, or 4): "
        if "%choice%"=="1" (
            echo Installing MongoDB using batch installer...
            call install_mongodb.bat
            if %errorlevel% neq 0 (
                echo MongoDB installation failed. Continuing with offline data.
                goto :continue_without_mongo
            )
        ) else if "%choice%"=="2" (
            echo Installing MongoDB using PowerShell installer...
            powershell -ExecutionPolicy Bypass -File install_mongodb.ps1
            if %errorlevel% neq 0 (
                echo MongoDB installation failed. Continuing with offline data.
                goto :continue_without_mongo
            )
        ) else if "%choice%"=="3" (
            echo Setting up existing MongoDB installation...
            call setup_mongodb.bat
            if %errorlevel% neq 0 (
                echo MongoDB setup failed. Continuing with offline data.
                goto :continue_without_mongo
            )
        ) else (
            echo Continuing with offline data mode.
            goto :continue_without_mongo
        )
    )
)

:check_mongo_connection
REM Verify MongoDB connection
echo Verifying MongoDB connection...
if exist mongodb_path.txt (
    set /p CUSTOM_MONGODB_PATH=<mongodb_path.txt
    echo Using custom MongoDB path: !CUSTOM_MONGODB_PATH!
    "!CUSTOM_MONGODB_PATH!\mongo.exe" --eval "db.stats()" >nul 2>&1
) else if exist "C:\Program Files\MongoDB\Server\*\bin\mongo.exe" (
    "C:\Program Files\MongoDB\Server\*\bin\mongo.exe" --eval "db.stats()" >nul 2>&1
) else if exist "D:\Program Files\MongoDB\Server\*\bin\mongo.exe" (
    "D:\Program Files\MongoDB\Server\*\bin\mongo.exe" --eval "db.stats()" >nul 2>&1
) else if exist "D:\MongoDB\Server\*\bin\mongo.exe" (
    "D:\MongoDB\Server\*\bin\mongo.exe" --eval "db.stats()" >nul 2>&1
) else (
    where mongo >nul 2>&1 && mongo --eval "db.stats()" >nul 2>&1
)
if %errorlevel% neq 0 (
    echo MongoDB connection failed. Continuing with offline data.
    goto :continue_without_mongo
)

echo MongoDB is running successfully!
goto :install_deps

:continue_without_mongo
echo.
echo WARNING: Running in offline mode. Some features may not work.
echo To enable full functionality, install MongoDB from: https://www.mongodb.com/try/download/community
echo.

:install_deps

REM Install backend dependencies if needed
echo Checking and installing backend dependencies...
cd backend && pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install backend dependencies.
    pause
    exit /b 1
)

REM Install frontend dependencies if needed
echo Checking and installing frontend dependencies...
cd .. && npm install
if %errorlevel% neq 0 (
    echo Failed to install frontend dependencies.
    pause
    exit /b 1
)

REM Try to seed the database with initial data
echo Seeding database with initial movie data...
cd backend && python seed.py
if %errorlevel% neq 0 (
    echo Database seeding failed. This is normal if MongoDB is not running.
    echo The app will work with offline data.
)

REM Start the backend server
echo Starting backend server...
start "Backend Server" cmd /k "cd backend && python run.py"

REM Wait a moment for backend to start
timeout /t 5 /nobreak > nul

REM Start the frontend server
echo Starting frontend server...
start "Frontend Server" cmd /k "npm run dev"

echo.
echo Both servers are starting...
echo Frontend will be available at http://localhost:5173
echo Backend API at http://localhost:5000
echo.
echo Note: If MongoDB is not running, the app will use offline/fallback data.
pause