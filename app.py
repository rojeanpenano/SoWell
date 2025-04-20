from flask import Flask, request, jsonify
from flask_cors import CORS
from firebase_init import db
from datetime import datetime
import pytz

app = Flask(__name__)
CORS(app)  # allow cross-origin requests (e.g., from Flutter or Postman)

# Root test route
@app.route('/')
def home():
    return jsonify({"message": "SoWell Flask API is running!"})

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


if __name__ == '__main__':
    app.run(debug=True)