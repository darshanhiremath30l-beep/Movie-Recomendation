# Movie Recommendation System Launcher
# This script starts both backend and frontend servers

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  🎬 Movie Recommendation System" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\activate.ps1")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Green
& "venv\Scripts\activate.ps1"

# Start backend server in background
Write-Host "🚀 Starting Flask backend server..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    Set-Location "backend"
    python run.py
}

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend development server in background
Write-Host "🎨 Starting React frontend server..." -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock {
    npm run dev
}

# Wait for frontend to start
Write-Host "⏳ Waiting for servers to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Open browser to frontend
Write-Host "🌐 Opening application in browser..." -ForegroundColor Green
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "✅ Application Started Successfully!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔗 Frontend: http://localhost:5173" -ForegroundColor Blue
Write-Host "🔗 Backend API: http://localhost:5000" -ForegroundColor Blue
Write-Host ""
Write-Host "📝 API Endpoints:" -ForegroundColor Magenta
Write-Host "  • Health Check: http://localhost:5000/api/health" -ForegroundColor White
Write-Host "  • Signup: POST http://localhost:5000/api/auth/signup" -ForegroundColor White
Write-Host "  • Login: POST http://localhost:5000/api/auth/login" -ForegroundColor White
Write-Host ""
Write-Host "🛑 To stop the application:" -ForegroundColor Red
Write-Host "  • Close this PowerShell window" -ForegroundColor White
Write-Host "  • Or stop the background jobs manually" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Keep the script running to show status
Write-Host "Press Ctrl+C to stop all servers and exit..." -ForegroundColor Yellow
try {
    # Monitor the jobs
    while ($true) {
        Start-Sleep -Seconds 10
        Write-Host "✅ Servers are running... (Press Ctrl+C to stop)" -ForegroundColor Green
    }
} finally {
    # Cleanup when script is terminated
    Write-Host "🛑 Stopping servers..." -ForegroundColor Red
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Stop-Job $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $frontendJob -ErrorAction SilentlyContinue
    Write-Host "✅ All servers stopped." -ForegroundColor Green
}