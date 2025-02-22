import os
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from pyfingerprint.pyfingerprint import PyFingerprint

app = Flask(__name__)
CORS(app)

# Load Environment Variables (Render-compatible)
SHEETDB_REGISTRATION_URL = os.getenv("SHEETDB_REGISTRATION_URL", "https://sheetdb.io/api/v1/lvg1wuw9n1k20")
SHEETDB_ATTENDANCE_URL = os.getenv("SHEETDB_ATTENDANCE_URL", "https://sheetdb.io/api/v1/lm3f46uz6mp8m")
DATABASE_URL = os.getenv("DATABASE_URL", "fingerprints.db")
PORT = int(os.getenv("PORT", 5000))  # Defaulting to 5000

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rollNumber TEXT UNIQUE,
            name TEXT,
            class TEXT,
            bloodGroup TEXT,
            academicYear TEXT,
            fingerprint TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Capture Fingerprint Function
def capture_fingerprint():
    try:
        fingerprint_sensor = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
        
        if not fingerprint_sensor.verifyPassword():
            raise ValueError("Fingerprint sensor password is incorrect!")

        print("Waiting for a finger...")
        while not fingerprint_sensor.readImage():
            pass

        fingerprint_sensor.convertImage(0x01)
        result = fingerprint_sensor.searchTemplate()
        positionNumber = result[0]

        if positionNumber >= 0:
            return str(positionNumber)

        fingerprint_sensor.createTemplate()
        fingerprintID = str(fingerprint_sensor.storeTemplate())
        return fingerprintID

    except Exception as e:
        print("Fingerprint error:", str(e))
        return None

# Register Student
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    rollNumber = data.get("rollNumber")
    name = data.get("name")
    classValue = data.get("class")
    bloodGroup = data.get("bloodGroup")
    academicYear = data.get("academicYear")

    fingerprint = capture_fingerprint()
    if fingerprint is None:
        return jsonify({"error": "Fingerprint scan failed"}), 400

    try:
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO students (rollNumber, name, class, bloodGroup, academicYear, fingerprint) VALUES (?, ?, ?, ?, ?, ?)", 
                       (rollNumber, name, classValue, bloodGroup, academicYear, fingerprint))
        conn.commit()
        conn.close()

        # Store in Google Sheets
        data["fingerprint"] = fingerprint
        requests.post(SHEETDB_REGISTRATION_URL, json={"data": data})

        return jsonify({"message": "Registration successful"})

    except sqlite3.IntegrityError:
        return jsonify({"error": "Student already registered or duplicate fingerprint"}), 400

# Mark Attendance
@app.route('/attendance', methods=['POST'])
def attendance():
    fingerprint = capture_fingerprint()

    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT rollNumber, name, class FROM students WHERE fingerprint=?", (fingerprint,))
    student = cursor.fetchone()
    conn.close()

    if not student:
        return jsonify({"error": "Fingerprint not recognized"}), 400

    rollNumber, name, classValue = student
    attendance_data = {
        "rollNumber": rollNumber,
        "name": name,
        "class": classValue,
        "time": request.json.get("time"),
        "date": request.json.get("date")
    }

    requests.post(SHEETDB_ATTENDANCE_URL, json={"data": attendance_data})
    return jsonify({"message": "Attendance recorded"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=PORT)
