@echo off
echo Searching for MongoDB installation...

echo Checking common installation locations:

REM Check C:\ drive locations
if exist "C:\Program Files\MongoDB\Server\*\bin\mongod.exe" (
    echo FOUND: MongoDB in C:\Program Files\MongoDB\Server\*
    for /d %%i in ("C:\Program Files\MongoDB\Server\*") do echo   Version: %%~ni
)

REM Check D:\ drive locations
if exist "D:\Program Files\MongoDB\Server\*\bin\mongod.exe" (
    echo FOUND: MongoDB in D:\Program Files\MongoDB\Server\*
    for /d %%i in ("D:\Program Files\MongoDB\Server\*") do echo   Version: %%~ni
)

if exist "D:\MongoDB\Server\*\bin\mongod.exe" (
    echo FOUND: MongoDB in D:\MongoDB\Server\*
    for /d %%i in ("D:\MongoDB\Server\*") do echo   Version: %%~ni
)

REM Search entire D:\ drive for mongod.exe
echo.
echo Searching entire D:\ drive for MongoDB (this may take a moment)...
for /r D:\ %%i in (mongod.exe) do (
    echo FOUND: %%i
    goto :found
)

:not_found
echo MongoDB not found in any standard locations on D:\ drive.

REM Check PATH
where mongod >nul 2>&1
if %errorlevel% equ 0 (
    echo FOUND: MongoDB in PATH
    where mongod
) else (
    echo NOT FOUND: MongoDB not in PATH
)

echo.
echo If MongoDB is installed but not found above, please:
echo 1. Tell me the exact installation path
echo 2. Or check Windows Services (services.msc) for MongoDB service
echo 3. Or run: mongod --version (if it's in PATH)
echo.
pause
exit /b 1

:found
echo.
echo MongoDB found! You can now run start.bat to use it with the app.
echo.
pause