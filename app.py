from flask import Flask, request, jsonify
from flask_cors import CORS
from firebase_init import db
from firebase_admin import auth, firestore
from datetime import datetime
import pytz

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string

# Define stopwords
filipino_stopwords = set([
    "akin", "aking", "ako", "alin", "am", "amin", "aming", "ang", "ano", "anumang", "apat", "at",
    "atin", "ating", "ay", "bababa", "bago", "bakit", "bawat", "bilang", "dahil", "dalawa", "dapat",
    "din", "dito", "doon", "gagawin", "gayunman", "ginagawa", "ginawa", "ginawang", "gumawa",
    "gusto", "habang", "hanggang", "hindi", "huwag", "iba", "ibaba", "ibabaw", "ibig", "ikaw",
    "ilagay", "ilalim", "ilan", "inyong", "isa", "isang", "itaas", "ito", "iyo", "iyon", "iyong",
    "ka", "kahit", "kailangan", "kailanman", "kami", "kanila", "kanilang", "kanino", "kanya",
    "kanyang", "kapag", "kapwa", "karamihan", "katiyakan", "katulad", "kaya", "kaysa", "ko", "kong",
    "kulang", "kumuha", "kung", "laban", "lahat", "lamang", "likod", "lima", "maaari", "maaaring",
    "maging", "mahusay", "makita", "marami", "marapat", "masyado", "may", "mayroon", "mga",
    "minsan", "mismo", "mula", "muli", "na", "nabanggit", "naging", "nagkaroon", "nais", "nakita",
    "namin", "napaka", "narito", "nasaan", "ng", "ngayon", "ni", "nila", "nilang", "nito", "niya",
    "niyang", "noon", "o", "pa", "paano", "pababa", "paggawa", "pagitan", "pagkakaroon",
    "pagkatapos", "palabas", "pamamagitan", "panahon", "pangalawa", "para", "paraan", "pareho",
    "pataas", "pero", "pumunta", "pumupunta", "sa", "saan", "sabi", "sabihin", "sarili", "sila",
    "sino", "siya", "tatlo", "tayo", "tulad", "tungkol", "una", "walang"
])
english_stopwords = set(stopwords.words("english"))
combined_stopwords = filipino_stopwords.union(english_stopwords)

    
def verify_firebase_token(request):
    """Verifies Firebase ID token from Authorization header."""
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None, "Missing Authorization header"

    if not auth_header.startswith("Bearer "):
        return None, "Invalid Authorization format"

    id_token = auth_header.split("Bearer ")[1]

    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]
        return uid, None
    except Exception as e:
        return None, f"Token verification failed: {str(e)}"


app = Flask(__name__)
CORS(app)  # allow cross-origin requests (e.g., from Flutter or Postman)

# Root test route
@app.route('/')
def home():
    return jsonify({"message": "SoWell Flask API is running!"})

# POST Route for User Registration:
@app.route('/api/user/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        uid = data.get("uid")
        name = data.get("name")
        location = data.get("location")
        is_farmer = data.get("is_farmer")

        if not uid or not name or location is None or is_farmer is None:
            return jsonify({"error": "Missing fields"}), 400

        user_data = {
            "name": name,
            "location": location,
            "is_farmer": is_farmer,
            "joined_at": datetime.utcnow()
        }

        # Create or overwrite the user document using uid
        db.collection("users").document(uid).set(user_data)

        return jsonify({"message": "User registered successfully", "uid": uid}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# GET Route for User Profile:
@app.route('/api/user/profile', methods=['GET'])
def get_profile():
    uid, error = verify_firebase_token(request)

    if error:
        return jsonify({"error": error}), 401

    user_doc = db.collection("users").document(uid).get()
    if not user_doc.exists:
        return jsonify({"error": "User not found"}), 404

    data = user_doc.to_dict()
    data["uid"] = uid
    return jsonify(data), 200

# POST Route for User Task:
@app.route('/api/user-task', methods=['POST'])
def create_user_task():
    try:
        data = request.json
        user_id = data.get("user_id")
        task = data.get("task")
        description = data.get("description")
        scheduled_str = data.get("scheduled_datetime")

        # Convert to datetime with PH timezone
        ph_time = pytz.timezone("Asia/Manila")
        scheduled_datetime = ph_time.localize(datetime.strptime(scheduled_str, "%Y-%m-%dT%H:%M"))

        new_task = {
            "user_id": user_id,
            "task": task,
            "description": description,
            "scheduled_datetime": scheduled_datetime,
            "created_at": datetime.utcnow(),
            "is_custom": False,
            "from_preset_id": None,
            "is_done": False
        }

        db.collection("user_calendar_events").add(new_task)

        return {"message": "Task created successfully"}, 201

    except Exception as e:
        return {"error": str(e)}, 500

# GET Route for User Task:
@app.route('/api/user-task', methods=['GET'])
def get_user_tasks():
    try:
        user_id = request.args.get("user_id")

        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400

        # Query Firestore for tasks by this user
        tasks_ref = (
            db.collection("user_calendar_events")
            .where("user_id", "==", user_id)
            .order_by("scheduled_datetime")
            .stream()
        )

        results = []
        for doc in tasks_ref:
            data = doc.to_dict()
            data["id"] = doc.id  # include the Firestore document ID
            # Convert datetime fields to ISO strings for JSON compatibility
            data["scheduled_datetime"] = data["scheduled_datetime"].isoformat()
            data["created_at"] = data["created_at"].isoformat()
            results.append(data)

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# PATCH (UPDATE) Route for User Task:
@app.route('/api/user-task/<task_id>', methods=['PATCH'])
def update_user_task(task_id):
    try:
        data = request.json
        updates = {}

        # Handle description
        if "description" in data:
            updates["description"] = data["description"]

        # Handle is_done
        if "is_done" in data:
            updates["is_done"] = data["is_done"]

        # Handle scheduled_datetime (convert if provided)
        if "scheduled_datetime" in data:
            ph_time = pytz.timezone("Asia/Manila")
            updates["scheduled_datetime"] = ph_time.localize(
                datetime.strptime(data["scheduled_datetime"], "%Y-%m-%dT%H:%M")
            )

        # Make sure something is being updated
        if not updates:
            return jsonify({"error": "No valid fields provided for update"}), 400

        # Update Firestore
        db.collection("user_calendar_events").document(task_id).update(updates)

        return jsonify({"message": "Task updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# DELETE Route for User Task:
@app.route('/api/user-task/<task_id>', methods=['DELETE'])
def delete_user_task(task_id):
    try:
        db.collection("user_calendar_events").document(task_id).delete()
        return jsonify({"message": "Task deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# GET Route for Rice Prices Data:
@app.route('/api/rice-prices', methods=['GET'])
def get_rice_prices():
    try:
        week_filter = request.args.get("week")
        latest_only = request.args.get("latest")

        # 🔍 Fetch specific week if ?week=2025-W15 is provided
        if week_filter:
            doc = db.collection("rice_prices").document(week_filter).get()
            if not doc.exists:
                return jsonify({"error": "Week not found"}), 404

            data = doc.to_dict()
            data["week_id"] = doc.id
            data["imported"] = data.get("imported", [])
            data["local"] = data.get("local", [])
            data["recorded_range"] = data.get("recorded_range", "")
            data["updated_at"] = data["updated_at"].isoformat()
            return jsonify(data), 200

        # 🆕 Fetch latest week only
        prices_ref = db.collection("rice_prices").stream()
        all_prices = []

        for doc in prices_ref:
            data = doc.to_dict()
            data["week_id"] = doc.id
            data["imported"] = data.get("imported", [])
            data["local"] = data.get("local", [])
            data["recorded_range"] = data.get("recorded_range", "")
            data["updated_at"] = data["updated_at"].isoformat()
            all_prices.append(data)

        # Sort by week_id (ascending)
        all_prices.sort(key=lambda x: x["week_id"])

        if latest_only and latest_only.lower() == "true":
            latest = all_prices[-1] if all_prices else {}
            return jsonify(latest), 200

        # Return all weeks by default
        return jsonify(all_prices), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# POST Route for Chatbot
@app.route('/api/chatbot/ask', methods=['POST'])
def chatbot_ask():
    try:
        data = request.get_json()
        user_id = data.get("user_id", "anonymous")  # optional user ID
        user_question = data.get("question", "").lower()

        # Tokenize and remove stopwords
        tokens = word_tokenize(user_question.translate(str.maketrans('', '', string.punctuation)))
        keywords = [t for t in tokens if t.isalpha() and t not in combined_stopwords]

        # Fetch from Firestore
        faqs = db.collection("chatbot_faqs").stream()

        best_match = None
        highest_score = 0

        for doc in faqs:
            faq = doc.to_dict()
            stored_keywords = faq.get("keywords", [])
            score = len(set(stored_keywords) & set(keywords))

            if score > highest_score:
                best_match = faq
                highest_score = score

        timestamp = datetime.utcnow()

        # Prepare log document
        log_data = {
            "user_id": user_id,
            "question": user_question,
            "match_score": highest_score,
            "timestamp": timestamp
        }

        if best_match and highest_score > 0:
            log_data["matched_question"] = best_match["question"]
            log_data["matched_answer"] = best_match["answer"]
            # Log match to Firestore
            db.collection("chatbot_logs").add(log_data)

            return jsonify({
                "question": best_match["question"],
                "answer": best_match["answer"],
                "match_score": highest_score
            })

        # If no match found
        log_data["matched_question"] = None
        log_data["matched_answer"] = None
        db.collection("chatbot_logs").add(log_data)

        return jsonify({"answer": "Paumanhin, wala akong mahanap na sagot sa iyong tanong."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# GET Route for Chatbot queries history
@app.route('/api/chatbot/history', methods=['GET'])
def chatbot_history():
    try:
        user_id = request.args.get("user_id")

        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400

        logs_ref = (
            db.collection("chatbot_logs")
            .where("user_id", "==", user_id)
            .order_by("timestamp", direction=firestore.Query.ASCENDING)
            .stream()
        )

        results = []
        for doc in logs_ref:
            log = doc.to_dict()
            log["timestamp"] = log["timestamp"].isoformat()
            results.append(log)

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)