@echo off
echo ============================================
echo   Testing MongoDB Connection...
echo ============================================
echo.

if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe backend\test_connection.py
) else if exist "backend\venv\Scripts\python.exe" (
    backend\venv\Scripts\python.exe backend\test_connection.py
) else (
    python backend\test_connection.py
)

echo.
pause

