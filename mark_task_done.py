from firebase_init import db

# Replace this with the actual document ID of the task
task_doc_id = "TaP1om3peiWMj0CP1X4P"

# Update the task to mark it as done
db.collection("user_calendar_events").document(task_doc_id).update({
    "is_done": True
})

print("Task marked as done successfully.")