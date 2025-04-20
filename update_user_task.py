from firebase_init import db
from datetime import datetime
import pytz

# Set timezone to Philippine Standard Time
ph_time = pytz.timezone("Asia/Manila")

# Replace with the actual document ID of the task
task_doc_id = "F8dRFjjr5pnKSaITNWmM"

# Define what to change
new_description = "Bagong pagtatanim schedule: ibalik sa punlaan"
new_scheduled_datetime = ph_time.localize(datetime(2025, 5, 1, 6, 0))  # May 1, 2025 at 6:00 AM

# Update the Firestore document
db.collection("user_calendar_events").document(task_doc_id).update({
    "description": new_description,
    "scheduled_datetime": new_scheduled_datetime
})

print("Task updated successfully.")