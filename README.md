# Task Dashboard

A full-stack task management dashboard with a FastAPI backend, React frontend, and iOS app.

---

## Project Structure

```
.
├── backend/          # FastAPI Python backend
│   ├── main.py       # App entry point
│   ├── models.py     # Database models
│   ├── database.py   # DB connection
│   ├── routers/      # API route handlers
│   │   ├── auth.py
│   │   ├── tasks.py
│   │   ├── employees.py
│   │   └── calendar.py
│   ├── utils.py
│   ├── seed.py       # Seed initial data
│   ├── seed_admin.py # Seed admin user
│   ├── requirements.txt
│   └── .env.example  # ← Copy to .env and fill in values
├── frontend/         # React + Vite frontend
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── services/api.js
│   └── package.json
├── ios_app/          # iOS Swift app source
├── TaskDashboard/    # Xcode project
├── Dockerfile
├── Procfile
└── requirements.txt
```

---

## Setup Instructions

### 1. Backend

```bash
cd backend

# Copy env template and fill in your values
cp .env.example .env
# Edit .env with your Gemini API key and SMTP credentials

# Install dependencies
pip install -r requirements.txt

# Initialize the database & seed admin user
python seed_admin.py

# Start the backend
uvicorn main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build
```

### 3. Deploy (Production)

The project includes a `Procfile` and `Dockerfile` for deployment.

- **Procfile**: For platforms like Railway, Render, or Heroku
- **Dockerfile**: For containerized deployments

Update `frontend/src/services/api.js` with your production backend URL before building.

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key |
| `SMTP_SERVER` | Email server (e.g. smtp.gmail.com) |
| `SMTP_PORT` | Email port (587) |
| `SMTP_USERNAME` | Sender email address |
| `SMTP_PASSWORD` | Email app password |
