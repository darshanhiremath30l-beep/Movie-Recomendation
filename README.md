# Movie Recommendation System

A full-stack movie recommendation application built with React (frontend) and Flask (backend).

## Quick Start (One-Click Launch)

**Double-click `run-app.bat`** (or `start.bat`) to start the entire application!

This automatically:
- Starts the Flask backend server (port 5000)
- Starts the React frontend development server (port 5173)
- Opens your browser to http://localhost:5173
- Connects to your configured database (or runs smoothly in local storage mode if not configured)

---

## Database Configuration (MongoDB)

The project supports both **MongoDB Atlas (Cloud)** and **Local MongoDB**. If MongoDB is not configured or offline, the app seamlessly runs in **Local Storage Mode** (`backend/data/local_db.json`) so it never crashes!

### How to Connect MongoDB Atlas (Recommended):
1. Create a free account at [MongoDB Atlas](https://cloud.mongodb.com/).
2. Create a free cluster (**M0 Free Tier**).
3. Under **Security > Network Access**, click **Add IP Address** -> **Allow Access From Anywhere** (`0.0.0.0/0`).
4. Under **Security > Database Access**, create a database user (note down your username and password).
5. Go to **Databases > Connect > Drivers > Python** and copy your connection string:
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. Open [`backend/.env`](backend/.env) and set your `MONGO_URI`:
   ```env
   MONGO_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   MONGO_DBNAME=cinematch_db
   ```
   *(Make sure to replace `<username>` and `<password>` with your real credentials)*.

### Testing Your Connection:
Double-click **`test-db.bat`** (or run `python backend/test_connection.py`) to verify your connection in 2 seconds!

### Seeding Initial Movies into MongoDB:
Once connected, populate initial movies by running:
```bash
cd backend
python seed.py
```

---

## Manual Start

### Backend:
```bash
cd backend
python run.py
```

### Frontend:
```bash
npm run dev
```

## Access Points

- **Frontend Application**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health
