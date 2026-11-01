from database import get_connection
from werkzeug.security import generate_password_hash

DOCTOR_EMAIL = "doctor@medicalchain.demo"
DOCTOR_PASSWORD = "Doctor@123"

PATIENT_PASSWORD = "Patient@123"

connection = get_connection()
cursor = connection.cursor(dictionary=True)

try:
    cursor.execute("""
        SELECT doctor_id FROM doctors
        WHERE license_number = %s
    """, ("DEMO-MC-001",))

    doctor = cursor.fetchone()

    if doctor:
        doctor_id = doctor["doctor_id"]
    else:
        cursor.execute("""
            INSERT INTO doctors (name, specialization, license_number)
            VALUES (%s, %s, %s)
        """, ("Dr. Amit Kumar", "General Medicine", "DEMO-MC-001"))

        doctor_id = cursor.lastrowid

    cursor.execute("""
        SELECT user_id FROM users WHERE email = %s
    """, (DOCTOR_EMAIL,))

    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO users (email, password_hash, role, doctor_id)
            VALUES (%s, %s, 'doctor', %s)
        """, (
            DOCTOR_EMAIL,
            generate_password_hash(DOCTOR_PASSWORD),
            doctor_id
        ))

    cursor.execute("SELECT patient_id, name FROM patients")
    patients = cursor.fetchall()

    for patient in patients:
        patient_id = patient["patient_id"]
        patient_email = f"patient{patient_id}@medicalchain.demo"

        cursor.execute("""
            SELECT user_id FROM users WHERE patient_id = %s
        """, (patient_id,))

        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO users (email, password_hash, role, patient_id)
                VALUES (%s, %s, 'patient', %s)
            """, (
                patient_email,
                generate_password_hash(PATIENT_PASSWORD),
                patient_id
            ))

        cursor.execute("""
            INSERT IGNORE INTO doctor_patient (doctor_id, patient_id)
            VALUES (%s, %s)
        """, (doctor_id, patient_id))

    connection.commit()

    print("\nDEMO ACCOUNTS CREATED SUCCESSFULLY")
    print("-----------------------------------")
    print("Doctor email:", DOCTOR_EMAIL)
    print("Doctor password:", DOCTOR_PASSWORD)
    print("\nPatient accounts:")

    for patient in patients:
        print(
            f"Patient: {patient['name']} | "
            f"Email: patient{patient['patient_id']}@medicalchain.demo | "
            f"Password: {PATIENT_PASSWORD}"
        )

finally:
    cursor.close()
    connection.close()
