import pymysql.cursors
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Database connection details
DB_HOST = 'meditrack-db.cdai64ksezzi.us-east-1.rds.amazonaws.com'
DB_USER = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = 'meditrack'

# Function to get a database connection
def get_db_connection():
    return pymysql.connect(host=DB_HOST,
                           user=DB_USER,
                           password=DB_PASSWORD,
                           db=DB_NAME,
                           port=3306,
                           cursorclass=pymysql.cursors.DictCursor)

# POST route to schedule a new appointment
@app.route('/appointments', methods=['POST'])
def schedule_appointment():
    data = request.json
    phone_number = data.get('phone_number')
    email = data.get('email')
    appointment_date = data.get('appointment_date')
    doctor_name = data.get('doctor_name')
    reason = data.get('reason')

    if not phone_number or not email or not appointment_date or not doctor_name or not reason:
        return jsonify({"error": "Missing required fields"}), 400

    # Check if patient exists
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM patients WHERE phone_number=%s", (phone_number,))
        patient = cursor.fetchone()

        if not patient:
            conn.close()
            return jsonify({"error": "Patient with phone number not found"}), 404

        patient_id = patient['id']

        # Schedule the appointment
        cursor.execute(
            "INSERT INTO appointments (patient_id, email, appointment_date, doctor_name, reason) VALUES (%s, %s, %s, %s, %s)",
            (patient_id, email, appointment_date, doctor_name, reason)
        )
        conn.commit()

    conn.close()
    return jsonify({"message": "Appointment scheduled"}), 201

# GET route to retrieve all appointments for a patient
@app.route('/appointments/<phone_number>', methods=['GET'])
def get_appointments(phone_number):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Get patient ID from phone number
        cursor.execute("SELECT id FROM patients WHERE phone_number=%s", (phone_number,))
        patient = cursor.fetchone()

        if not patient:
            conn.close()
            return jsonify({"error": "Patient with phone number not found"}), 404

        patient_id = patient['id']

        # Retrieve appointments
        cursor.execute("SELECT * FROM appointments WHERE patient_id=%s", (patient_id,))
        appointments = cursor.fetchall()

    conn.close()
    return jsonify({"appointments": appointments})

# PUT route to update an appointment by ID
@app.route('/appointments/<int:appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    data = request.json
    email = data.get('email')
    appointment_date = data.get('appointment_date')
    doctor_name = data.get('doctor_name')
    reason = data.get('reason')

    if not email and not appointment_date and not doctor_name and not reason:
        return jsonify({"error": "No fields to update"}), 400

    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE appointments SET email=%s, appointment_date=%s, doctor_name=%s, reason=%s WHERE id=%s",
            (email, appointment_date, doctor_name, reason, appointment_id)
        )
        conn.commit()

    conn.close()
    return jsonify({"message": "Appointment updated"}), 200

# DELETE route to cancel an appointment by ID
@app.route('/appointments/<int:appointment_id>', methods=['DELETE'])
def cancel_appointment(appointment_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM appointments WHERE id=%s", (appointment_id,))
        conn.commit()

    conn.close()
    return jsonify({"message": "Appointment canceled"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
