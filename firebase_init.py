import firebase_admin
from firebase_admin import credentials, firestore

# Load your service account key (make sure it's in the same folder)
cred = credentials.Certificate("sowell-key.json")

# Initialize Firebase app
firebase_admin.initialize_app(cred)

# Get Firestore database client
db = firestore.client()

# Test print
print("Firebase connection established. Firestore is ready to use.")