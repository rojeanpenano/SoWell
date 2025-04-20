from firebase_init import db
from datetime import datetime

# Example user profile data (replace these values as needed)
user_data = {
    "uid": "sowell",  # Usually comes from Firebase Auth
    "name": "SoWell App",
    "location": "Dasmarinas City",
    "is_farmer": True,
    "joined_at": datetime.utcnow()
}

# Save to Firestore under the 'users' collection
db.collection("users").document(user_data["uid"]).set(user_data)

print("User profile uploaded successfully to Firestore.")