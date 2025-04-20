from firebase_init import db

# User ID to filter
user_id = "sowell"

# Fetch tasks for that user, sorted by scheduled_datetime (nearest first)
user_tasks = (
    db.collection("user_calendar_events")
    .where("user_id", "==", user_id)
    .order_by("scheduled_datetime")
    .stream()
)

for doc in user_tasks:
    data = doc.to_dict()
    print(f"Doc ID: {doc.id}")

# Display the results
print(f"Tasks for user: {user_id}")
for doc in user_tasks:
    data = doc.to_dict()
    print(f"- {data.get('task')} ({data.get('scheduled_datetime')})")
    print(f"  {data.get('description')}")
    print(f"  Done? {data.get('is_done')}\n")