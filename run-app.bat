@echo off
echo ============================================
echo   🎬 Movie Recommendation System
echo ============================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo Please run setup first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Start backend server in background
echo 🚀 Starting Flask backend server...
start "Flask Backend" cmd /c "cd backend && python run.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend development server in background
echo 🎨 Starting React frontend server...
start "React Frontend" cmd /c "npm run dev"

REM Wait for frontend to start
echo ⏳ Waiting for servers to initialize...
timeout /t 5 /nobreak >nul

REM Open browser to frontend
echo 🌐 Opening application in browser...
start http://localhost:5173

echo.
echo ============================================
echo ✅ Application Started Successfully!
echo ============================================
echo.
echo 🔗 Frontend: http://localhost:5173
echo 🔗 Backend API: http://localhost:5000
echo.
echo 📝 API Endpoints:
echo   • Health Check: http://localhost:5000/api/health
echo   • Signup: POST http://localhost:5000/api/auth/signup
echo   • Login: POST http://localhost:5000/api/auth/login
echo.
echo 🛑 To stop the application:
echo   • Close the terminal windows or press Ctrl+C
echo ============================================
echo.
pause