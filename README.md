# Movie Recommendation System

A full-stack movie recommendation application built with React (frontend) and Flask (backend).

## 🚀 Quick Start (One-Click Launch)

**Just double-click `run-app.bat`** to start the entire application!

This automatically:
- ✅ Starts Flask backend server (port 5000)
- ✅ Starts React frontend server (port 5173)
- ✅ Opens your browser to the application
- ✅ Shows connection details and API endpoints

For detailed setup instructions, see [QUICKSTART.md](QUICKSTART.md)

## Features

- User authentication
- Movie search and details
- Personalized recommendations
- Watchlist management
- User profiles

## Prerequisites

- Node.js (for frontend)
- Python 3.8+ (for backend)
- MongoDB (for database - can be installed automatically)

### MongoDB Installation

**Option 1: Automatic Installation (Recommended)**
- Run `start.bat` and choose option 1 (batch) or 2 (PowerShell) when prompted

**Option 2: Custom Installation Path**
If you installed MongoDB in a custom location:
- Run `start.bat` and choose option 3 to enter your MongoDB path

**Option 3: Manual Installation**
1. Download MongoDB Community Edition from: https://www.mongodb.com/try/download/community
2. Run the installer and follow the setup wizard
3. Create data directory: `mkdir C:\data\db`
4. Start MongoDB service or run manually: `"C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe" --dbpath "C:\data\db"`

### Features Requiring MongoDB
- User authentication and profiles
- Personalized movie recommendations
- Watchlist and user interactions
- Real-time movie search (OMDB API integration)
- Persistent data storage

**Without MongoDB**: App runs with sample offline data for browsing and basic functionality.

### Testing MongoDB Installation
Run `test_mongodb.bat` to verify MongoDB is working correctly.

### Installation

1. Clone the repository
2. Install frontend dependencies:
   ```bash
   npm install
   ```
3. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

### Running the Application

**Single Click Start (Windows):**
Double-click the `start.bat` file in the root directory to start both frontend and backend servers.

**Manual Start:**

1. Start the backend:
   ```bash
   cd backend
   python run.py
   ```

2. Start the frontend (in a new terminal):
   ```bash
   npm run dev
   ```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000

## Project Structure

- `src/` - React frontend code
- `backend/` - Flask backend API
- `public/` - Static assets

## Technologies Used

- Frontend: React, Vite, React Router
- Backend: Flask, MongoDB, scikit-learn
- Styling: CSS modules
