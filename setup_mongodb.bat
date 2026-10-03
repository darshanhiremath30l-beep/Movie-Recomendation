@echo off
echo MongoDB Path Configuration
echo.

echo Please enter the full path to your MongoDB bin directory.
echo Example: D:\MongoDB\Server\7.0\bin
echo Or: D:\Program Files\MongoDB\Server\7.0\bin
echo.
set /p MONGODB_PATH="MongoDB bin path: "

REM Validate the path
if not exist "%MONGODB_PATH%\mongod.exe" (
    echo ERROR: mongod.exe not found at %MONGODB_PATH%
    echo Please check the path and try again.
    pause
    exit /b 1
)

if not exist "%MONGODB_PATH%\mongo.exe" (
    echo ERROR: mongo.exe not found at %MONGODB_PATH%
    echo Please check the path and try again.
    pause
    exit /b 1
)

echo MongoDB found at: %MONGODB_PATH%

REM Test MongoDB connection
echo Testing MongoDB connection...
"%MONGODB_PATH%\mongo.exe" --eval "db.runCommand('ping')" >nul 2>&1
if %errorlevel% equ 0 (
    echo SUCCESS: MongoDB is running and accessible!
) else (
    echo MongoDB is not running. Attempting to start it...
    REM Create data directory if it doesn't exist
    if not exist "C:\data\db" mkdir "C:\data\db"
    REM Try to start MongoDB
    start "MongoDB" "%MONGODB_PATH%\mongod.exe" --dbpath "C:\data\db"
    timeout /t 3 /nobreak > nul

    REM Test again
    "%MONGODB_PATH%\mongo.exe" --eval "db.runCommand('ping')" >nul 2>&1
    if %errorlevel% equ 0 (
        echo SUCCESS: MongoDB started successfully!
    ) else (
        echo WARNING: Could not start MongoDB automatically.
        echo You may need to start it manually or check Windows Services.
    )
)

REM Save the path for future use
echo %MONGODB_PATH% > mongodb_path.txt
echo MongoDB path saved to mongodb_path.txt

echo.
echo Configuration complete! You can now run start.bat
pause