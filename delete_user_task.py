from firebase_init import db

# Replace this with the actual document ID of the task
task_doc_id = "TaP1om3peiWMj0CP1X4P"

# Delete the task from Firestore
db.collection("user_calendar_events").document(task_doc_id).delete()

print("Task deleted successfully from Firestore.")
