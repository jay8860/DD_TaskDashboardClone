# ingester.py
# Google Sheets sync has been removed.
# All tasks are managed exclusively through the local SQLite database.

def sync_data(db):
    return {"message": "No-op: Google Sheets sync removed."}

def update_sheet_task(task_number: str, updates: dict):
    return {"status": "skipped", "reason": "Google Sheets sync removed."}

def delete_sheet_task(task_number: str):
    return {"status": "skipped", "reason": "Google Sheets sync removed."}

def push_portal_to_sheet(db):
    return {"status": "skipped", "reason": "Google Sheets sync removed."}
