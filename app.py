from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from pyfingerprint.pyfingerprint import PyFingerprint

app = Flask(__name__)
CORS(app)

SHEETDB_REGISTRATION_URL = "https://sheetdb.io/api/v1/lvg1wuw9n1k20"
SHEETDB_ATTENDANCE_URL = "https://sheetdb.io/api/v1/lm3f46uz6mp8m"

fingerprint_database = {}

def capture_fingerprint():
    try:
        fingerprint_sensor = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

        if fingerprint_sensor.verifyPassword() == False:
            raise ValueError('Fingerprint sensor password is incorrect!')

        print('Waiting for a finger...')
        while not fingerprint_sensor.readImage():
            pass

        fingerprint_sensor.convertImage(0x01)
        result = fingerprint_sensor.searchTemplate()
        positionNumber = result[0]

        if positionNumber >= 0:
            return str(positionNumber)  # Return fingerprint ID

        fingerprint_sensor.createTemplate()
        fingerprintID = str(fingerprint_sensor.storeTemplate())
        return fingerprintID

    except Exception as e:
        print('Fingerprint error:', str(e))
        return None

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    student_id = data.get("rollNumber")

    fingerprint = capture_fingerprint()  # Capture fingerprint from scanner
    if fingerprint is None:
        print("Fingerprint capture failed")
        return jsonify({"error": "Fingerprint scan failed"}), 400

    data["fingerprint"] = fingerprint  # Store fingerprint ID
    fingerprint_database[student_id] = data  # Save student data

    try:
        response = requests.post(SHEETDB_REGISTRATION_URL, json={"data": data})
        response.raise_for_status()  # Raises HTTPError for bad responses
        return jsonify({"message": "Registration successful", "response": response.json()})
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return jsonify({"error": "Error communicating with the registration API"}), 500

@app.route('/attendance', methods=['POST'])
def attendance():
    fingerprint = capture_fingerprint()

    matched_student = None
    for student_id, stored_data in fingerprint_database.items():
        if stored_data["fingerprint"] == fingerprint:
            matched_student = student_id
            break

    if not matched_student:
        return jsonify({"error": "Fingerprint not recognized"}), 400

    attendance_data = {
        "rollNumber": matched_student,
        "name": fingerprint_database[matched_student]["name"],
        "class": fingerprint_database[matched_student]["class"],
        "time": request.json.get("time"),
        "date": request.json.get("date")
    }

    response = requests.post(SHEETDB_ATTENDANCE_URL, json={"data": attendance_data})
    return jsonify({"message": "Attendance recorded", "response": response.json()})
