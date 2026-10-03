# Movie Recommendation System - Quick Start

## 🚀 One-Click Launch

**Double-click `run-app.bat`** to start the entire application!

This will automatically:
- ✅ Start the Flask backend server (port 5000)
- ✅ Start the React frontend server (port 5173)
- ✅ Open your browser to the application
- ✅ Show connection details and API endpoints

## 📋 Prerequisites

Make sure you have completed the initial setup:

1. **Python Environment**: Virtual environment created and activated
2. **Dependencies**: All packages installed (`pip install -r backend/requirements.txt`)
3. **MongoDB**: Connected to MongoDB Atlas (configured in `backend/.env`)
4. **Node.js**: Frontend dependencies installed (`npm install`)

## 🔧 Manual Start (Alternative)

If you prefer to start services individually:

### Backend Only
```bash
cd backend
python run.py
```

### Frontend Only
```bash
npm run dev
```

### Full Application
```bash
# Terminal 1 - Backend
cd backend && python run.py

# Terminal 2 - Frontend
npm run dev
```

## 🌐 Access Points

- **Frontend Application**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

## 🛑 Stopping the Application

- Close the terminal windows that opened
- Or press `Ctrl+C` in each terminal

## 🔍 Troubleshooting

- **Port conflicts**: Make sure ports 5000 and 5173 are available
- **MongoDB issues**: Check your `backend/.env` file and Atlas connection
- **Python errors**: Ensure virtual environment is activated
- **Node errors**: Run `npm install` to ensure dependencies are installed