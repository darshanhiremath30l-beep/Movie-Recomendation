@echo off
echo Testing MongoDB installation...

REM Check if MongoDB binaries exist in common locations
set MONGO_EXE=
if exist "C:\Program Files\MongoDB\Server\*\bin\mongo.exe" (
    for /d %%i in ("C:\Program Files\MongoDB\Server\*") do set MONGO_EXE="%%i\bin\mongo.exe"
) else if exist "D:\Program Files\MongoDB\Server\*\bin\mongo.exe" (
    for /d %%i in ("D:\Program Files\MongoDB\Server\*") do set MONGO_EXE="%%i\bin\mongo.exe"
) else if exist "D:\MongoDB\Server\*\bin\mongo.exe" (
    for /d %%i in ("D:\MongoDB\Server\*") do set MONGO_EXE="%%i\bin\mongo.exe"
) else (
    where mongo >nul 2>&1 && set MONGO_EXE=mongo
)

if defined MONGO_EXE (
    echo MongoDB binaries found at: %MONGO_EXE%

    REM Try to connect to MongoDB
    %MONGO_EXE% --eval "db.runCommand('ping')" >nul 2>&1
    if %errorlevel% equ 0 (
        echo MongoDB connection successful!
        %MONGO_EXE% --eval "db.createCollection('test')" >nul 2>&1
        if %errorlevel% equ 0 (
            echo Database operations working.
        ) else (
            echo Database operations failed.
        )
    ) else (
        echo MongoDB connection failed. Service may not be running.
        echo Try starting MongoDB manually or check if it's running as a service.
    )
) else (
    echo MongoDB binaries not found in any of these locations:
    echo - C:\Program Files\MongoDB\Server\*\bin\mongo.exe
    echo - D:\Program Files\MongoDB\Server\*\bin\mongo.exe
    echo - D:\MongoDB\Server\*\bin\mongo.exe
    echo - PATH environment variable
    echo.
    echo Please check your MongoDB installation or run start.bat to install it.
)

pause