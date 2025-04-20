from firebase_init import db
from datetime import datetime
import pytz

# Set timezone to Philippine Standard Time
ph_time = pytz.timezone("Asia/Manila")

# Simulated user assigning a preset task to their schedule
user_id = "sowell"
selected_task = {
    "task": "Magtanim",
    "description": "Ilipat ang punla mula punlaan papuntang palayan kapag sapat na ang edad nito.",
    "scheduled_datetime": ph_time.localize(datetime(2025, 4, 25, 6, 30))  # April 25, 2025 at 6:30 AM
}

# Task object to be uploaded
user_task = {
    "user_id": user_id,
    "task": selected_task["task"],
    "description": selected_task["description"],
    "scheduled_datetime": selected_task["scheduled_datetime"],
    "created_at": datetime.utcnow(),
    "is_custom": False,
    "from_preset_id": None,
    "is_done": False
}

# Save to Firestore
db.collection("user_calendar_events").add(user_task)

print("User-specific calendar task created successfully in Firestore.")
