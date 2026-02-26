from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import engine, Base, SessionLocal
from routers import tasks, auth
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Tables
Base.metadata.create_all(bind=engine)

# --- Auto-Migration: Add columns if missing ---
from sqlalchemy import text
def run_migrations():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("PRAGMA table_info(tasks)"))
            columns = [row[1] for row in result.fetchall()]

            if "is_pinned" not in columns:
                print("🔄 Migration: Adding 'is_pinned' column...")
                connection.execute(text("ALTER TABLE tasks ADD COLUMN is_pinned INTEGER DEFAULT 0"))
                connection.commit()

            if "scheduled_date" not in columns:
                print("🔄 Migration: Adding 'scheduled_date' column...")
                connection.execute(text("ALTER TABLE tasks ADD COLUMN scheduled_date DATE"))
                connection.commit()

            if "position" not in columns:
                print("🔄 Migration: Adding 'position' column...")
                connection.execute(text("ALTER TABLE tasks ADD COLUMN position FLOAT DEFAULT 0.0"))
                connection.commit()

            if "scheduled_time" not in columns:
                print("🔄 Migration: Adding 'scheduled_time' column...")
                connection.execute(text("ALTER TABLE tasks ADD COLUMN scheduled_time VARCHAR"))
                connection.commit()

            if "attachment_data" not in columns:
                print("🔄 Migration: Adding 'attachment_data' column...")
                connection.execute(text("ALTER TABLE tasks ADD COLUMN attachment_data TEXT"))
                connection.commit()

            print("✅ Migrations complete.")
    except Exception as e:
        print(f"❌ Migration Error: {e}")

run_migrations()

# Seed Admin User
from seed_auth import seed_admin
seed_admin()

app = FastAPI(title="Task Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://127.0.0.1:5174", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(auth.router, prefix="/api")

from routers import employees
app.include_router(employees.router, prefix="/api/employees", tags=["employees"])

from routers import calendar
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])

# Serve React Frontend (Single Service Mode)
frontend_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../frontend/dist")

if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        if full_path.startswith("api"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="API Endpoint not found")
        return FileResponse(os.path.join(frontend_dist, "index.html"))

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Task Dashboard API"}
