import os
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from mysql.connector import IntegrityError

from database import get_connection
from blockchain import (
    calculate_record_hash,
    store_hash_on_blockchain,
    verify_hash_on_blockchain,
)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "MedicalChain-Demo-Secret-Change-Before-Production")

DEPARTMENTS = [
    "General Medicine", "Cardiology", "Dermatology", "Neurology",
    "Orthopedics", "Pediatrics", "Ophthalmology", "Gynecology", "Psychiatry",
]

DISEASE_CATEGORIES = {
    "General Health": "General Medicine",
    "General Medicine": "General Medicine",
    "Heart Problems": "Cardiology",
    "Cardiology": "Cardiology",
    "Skin Problems": "Dermatology",
    "Dermatology": "Dermatology",
    "Brain and Nerve Problems": "Neurology",
    "Neurology": "Neurology",
    "Bone and Joint Problems": "Orthopedics",
    "Orthopedics": "Orthopedics",
    "Child Healthcare": "Pediatrics",
    "Pediatrics": "Pediatrics",
    "Eye Problems": "Ophthalmology",
    "Ophthalmology": "Ophthalmology",
    "Women's Health": "Gynecology",
    "Gynecology": "Gynecology",
    "Mental Health": "Psychiatry",
    "Psychiatry": "Psychiatry",
}


def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in first.", "error")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapped


def role_required(role):
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if not session.get("user_id"):
                flash("Please log in first.", "error")
                return redirect(url_for("login"))
            if session.get("role") != role:
                flash("You are not authorized to access that page.", "error")
                return redirect(url_for("dashboard"))
            return fn(*args, **kwargs)
        return wrapped
    return decorator


def department_for_category(category):
    department = DISEASE_CATEGORIES.get(category)
    if not department:
        raise ValueError("Please select a valid disease category.")
    return department


def choose_least_loaded_doctor(cursor, department):
    cursor.execute("""
        SELECT
            d.doctor_id,
            COUNT(
                CASE WHEN dp.status IN ('pending', 'in_progress')
                THEN dp.assignment_id END
            ) AS workload
        FROM doctors d
        LEFT JOIN doctor_patient dp ON dp.doctor_id = d.doctor_id
        WHERE d.department = %s
        GROUP BY d.doctor_id
        ORDER BY workload ASC, d.doctor_id ASC
        LIMIT 1
    """, (department,))
    doctor = cursor.fetchone()
    if not doctor:
        raise ValueError(f"No doctor is registered in {department}. Please register a doctor first.")
    return doctor["doctor_id"]


def assign_existing_unassigned_patients():
    """Assign existing unassigned patients using the same least-workload rule."""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    assigned = []
    try:
        cursor.execute("""
            SELECT p.patient_id, p.disease_category
            FROM patients p
            LEFT JOIN doctor_patient dp ON dp.patient_id = p.patient_id
            WHERE dp.assignment_id IS NULL
            ORDER BY p.patient_id
        """)
        patients = cursor.fetchall()
        for patient in patients:
            department = department_for_category(patient["disease_category"])
            doctor_id = choose_least_loaded_doctor(cursor, department)
            cursor.execute("""
                INSERT INTO doctor_patient (doctor_id, patient_id, status)
                VALUES (%s, %s, 'pending')
            """, (doctor_id, patient["patient_id"]))
            assigned.append((patient["patient_id"], doctor_id))
        connection.commit()
        return assigned
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def create_patient_and_assign(cursor, name, age, gender, phone, email, password, category):
    department = department_for_category(category)
    cursor.execute("""
        INSERT INTO patients (name, age, gender, phone, disease_category)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, age, gender or None, phone or None, department))
    patient_id = cursor.lastrowid

    doctor_id = choose_least_loaded_doctor(cursor, department)
    cursor.execute("""
        INSERT INTO doctor_patient (doctor_id, patient_id, status)
        VALUES (%s, %s, 'pending')
    """, (doctor_id, patient_id))

    cursor.execute("""
        INSERT INTO users (email, password_hash, role, patient_id)
        VALUES (%s, %s, 'patient', %s)
    """, (email, generate_password_hash(password), patient_id))
    return patient_id, doctor_id


@app.route("/")
def index():
    return redirect(url_for("dashboard") if session.get("user_id") else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT u.user_id, u.email, u.password_hash, u.role,
                       u.patient_id, u.doctor_id,
                       p.name AS patient_name, d.name AS doctor_name
                FROM users u
                LEFT JOIN patients p ON p.patient_id = u.patient_id
                LEFT JOIN doctors d ON d.doctor_id = u.doctor_id
                WHERE u.email = %s
            """, (email,))
            user = cursor.fetchone()
        finally:
            cursor.close()
            connection.close()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session.update({
                "user_id": user["user_id"],
                "email": user["email"],
                "role": user["role"],
                "patient_id": user["patient_id"],
                "doctor_id": user["doctor_id"],
                "display_name": user["doctor_name"] if user["role"] == "doctor" else user["patient_name"],
            })
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")


@app.route("/logout", methods=["POST", "GET"])
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    return redirect(url_for("doctor_dashboard" if session["role"] == "doctor" else "patient_dashboard"))


@app.route("/register/doctor", methods=["GET", "POST"])
def register_doctor():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        qualification = request.form.get("qualification", "").strip()
        specialization = request.form.get("specialization", "").strip()
        department = request.form.get("department", "").strip()
        license_number = request.form.get("license_number", "").strip()
        experience_raw = request.form.get("years_experience", "0").strip()

        if not all([name, email, password, qualification, specialization, department, license_number]):
            flash("Please complete all required fields.", "error")
            return render_template("register_doctor.html", departments=DEPARTMENTS)
        if department not in DEPARTMENTS:
            flash("Select a valid department.", "error")
            return render_template("register_doctor.html", departments=DEPARTMENTS)
        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
            return render_template("register_doctor.html", departments=DEPARTMENTS)
        try:
            experience = int(experience_raw)
            if experience < 0 or experience > 70:
                raise ValueError
        except ValueError:
            flash("Experience must be a number between 0 and 70.", "error")
            return render_template("register_doctor.html", departments=DEPARTMENTS)

        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO doctors
                    (name, specialization, license_number, department, qualification, years_experience)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, specialization, license_number, department, qualification, experience))
            doctor_id = cursor.lastrowid
            cursor.execute("""
                INSERT INTO users (email, password_hash, role, doctor_id)
                VALUES (%s, %s, 'doctor', %s)
            """, (email, generate_password_hash(password), doctor_id))
            connection.commit()
            flash("Doctor account created. You can now log in.", "success")
            return redirect(url_for("login"))
        except IntegrityError:
            connection.rollback()
            flash("Email or license number is already registered.", "error")
        except Exception as exc:
            connection.rollback()
            flash("Registration failed: " + str(exc), "error")
        finally:
            cursor.close()
            connection.close()
    return render_template("register_doctor.html", departments=DEPARTMENTS)


@app.route("/register/patient", methods=["GET", "POST"])
def register_patient():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        age_raw = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()
        phone = request.form.get("phone", "").strip()
        category = request.form.get("disease_category", "").strip()

        if not all([name, email, password, age_raw, category]):
            flash("Name, email, password, age and disease category are required.", "error")
            return render_template("register_patient.html", categories=list(DISEASE_CATEGORIES.keys()))
        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
            return render_template("register_patient.html", categories=list(DISEASE_CATEGORIES.keys()))
        try:
            age = int(age_raw)
            if not 0 <= age <= 130:
                raise ValueError
            department = department_for_category(category)
            connection = get_connection()
            cursor = connection.cursor()
            try:
                patient_id, doctor_id = create_patient_and_assign(
                    cursor, name, age, gender, phone, email, password, category
                )
                connection.commit()
                flash(f"Patient account created. Patient ID: {patient_id}. Assigned doctor ID: {doctor_id}.", "success")
                return redirect(url_for("login"))
            except IntegrityError:
                connection.rollback()
                flash("This email is already registered.", "error")
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()
                connection.close()
        except ValueError as exc:
            flash(str(exc) if str(exc) else "Enter a valid age.", "error")
        except Exception as exc:
            flash("Patient registration failed: " + str(exc), "error")
    return render_template("register_patient.html", categories=list(DISEASE_CATEGORIES.keys()))


@app.route("/doctor")
@role_required("doctor")
def doctor_dashboard():
    doctor_id = session["doctor_id"]
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) AS total FROM doctor_patient WHERE doctor_id=%s", (doctor_id,))
        total_patients = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(*) AS total FROM medical_records WHERE doctor_id=%s", (doctor_id,))
        total_records = cursor.fetchone()["total"]
        cursor.execute("""
            SELECT p.patient_id, p.name, p.age, p.gender, p.phone,
                   p.disease_category, dp.status, dp.assigned_at
            FROM patients p
            JOIN doctor_patient dp ON dp.patient_id = p.patient_id
            WHERE dp.doctor_id = %s
            ORDER BY p.name
        """, (doctor_id,))
        patients = cursor.fetchall()
        cursor.execute("""
            SELECT mr.record_id, mr.diagnosis, mr.doctor_name, mr.created_at,
                   p.name AS patient_name
            FROM medical_records mr
            JOIN patients p ON p.patient_id = mr.patient_id
            JOIN doctor_patient dp
              ON dp.patient_id = mr.patient_id AND dp.doctor_id = mr.doctor_id
            WHERE mr.doctor_id = %s
            ORDER BY mr.record_id DESC
            LIMIT 6
        """, (doctor_id,))
        recent_records = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()
    return render_template("doctor_dashboard.html", total_patients=total_patients,
                           total_records=total_records, patients=patients,
                           recent_records=recent_records)


@app.route("/doctor/patients/add", methods=["GET", "POST"])
@role_required("doctor")
def add_patient():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        age_raw = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()
        phone = request.form.get("phone", "").strip()
        category = request.form.get("disease_category", "General Health").strip()
        try:
            age = int(age_raw) if age_raw else None
            if age is not None and not 0 <= age <= 130:
                raise ValueError("Age must be between 0 and 130.")
            if not all([name, email, password]) or len(password) < 8:
                raise ValueError("Name, email and a password of at least 8 characters are required.")
            connection = get_connection()
            cursor = connection.cursor()
            try:
                patient_id, doctor_id = create_patient_and_assign(
                    cursor, name, age, gender, phone, email, password, category
                )
                connection.commit()
                flash(f"Patient registered and assigned by department workload. Patient ID: {patient_id}; Doctor ID: {doctor_id}.", "success")
                return redirect(url_for("doctor_dashboard"))
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()
                connection.close()
        except Exception as exc:
            flash("Could not register patient: " + str(exc), "error")
    return render_template("add_patient.html", categories=list(DISEASE_CATEGORIES.keys()))


@app.route("/doctor/records/add", methods=["GET", "POST"])
@role_required("doctor")
def add_record():
    doctor_id = session["doctor_id"]
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT p.patient_id, p.name
            FROM patients p
            JOIN doctor_patient dp ON dp.patient_id=p.patient_id
            WHERE dp.doctor_id=%s
            ORDER BY p.name
        """, (doctor_id,))
        patients = cursor.fetchall()
        cursor.execute("SELECT name FROM doctors WHERE doctor_id=%s", (doctor_id,))
        doctor = cursor.fetchone()
        doctor_name = doctor["name"] if doctor else "Doctor"
    finally:
        cursor.close()
        connection.close()

    if request.method == "POST":
        try:
            patient_id = int(request.form.get("patient_id", "0"))
            diagnosis = request.form.get("diagnosis", "").strip()
            prescription = request.form.get("prescription", "").strip()
            if not diagnosis:
                raise ValueError("Diagnosis is required.")
            connection = get_connection()
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    SELECT assignment_id FROM doctor_patient
                    WHERE doctor_id=%s AND patient_id=%s
                """, (doctor_id, patient_id))
                if not cursor.fetchone():
                    raise PermissionError("This patient is not assigned to your account.")
                cursor.execute("""
                    INSERT INTO medical_records
                        (patient_id, doctor_id, diagnosis, prescription, doctor_name)
                    VALUES (%s, %s, %s, %s, %s)
                """, (patient_id, doctor_id, diagnosis, prescription, doctor_name))
                record_id = cursor.lastrowid
                connection.commit()

                # Keep the existing hash payload format for compatibility with
                # earlier records; doctor ownership is separately enforced in MySQL.
                record_data = {
                    "record_id": int(record_id),
                    "patient_id": int(patient_id),
                    "diagnosis": diagnosis,
                    "prescription": prescription,
                    "doctor_name": doctor_name,
                }
                try:
                    record_hash = calculate_record_hash(record_data)
                    tx_hash = store_hash_on_blockchain(record_id, record_hash)
                    cursor.execute("""
                        UPDATE medical_records
                        SET record_hash=%s, transaction_hash=%s
                        WHERE record_id=%s AND doctor_id=%s
                    """, (record_hash, tx_hash, record_id, doctor_id))
                    cursor.execute("""
                        UPDATE doctor_patient SET status='in_progress'
                        WHERE doctor_id=%s AND patient_id=%s AND status='pending'
                    """, (doctor_id, patient_id))
                    connection.commit()
                    flash(f"Record #{record_id} saved and secured on blockchain.", "success")
                except Exception as chain_exc:
                    flash(f"Record saved in MySQL, but blockchain storage failed: {chain_exc}", "error")
                return redirect(url_for("records"))
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()
                connection.close()
        except Exception as exc:
            flash("Could not save record: " + str(exc), "error")
    return render_template("add_record.html", patients=patients)


@app.route("/patient")
@role_required("patient")
def patient_dashboard():
    patient_id = session["patient_id"]
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT p.patient_id, p.name, p.age, p.gender, p.phone,
                   p.disease_category, p.created_at,
                   d.name AS assigned_doctor, d.department
            FROM patients p
            LEFT JOIN doctor_patient dp ON dp.patient_id=p.patient_id
            LEFT JOIN doctors d ON d.doctor_id=dp.doctor_id
            WHERE p.patient_id=%s
        """, (patient_id,))
        patient = cursor.fetchone()
        cursor.execute("""
            SELECT record_id, diagnosis, prescription, doctor_name,
                   record_hash, created_at
            FROM medical_records
            WHERE patient_id=%s
            ORDER BY record_id DESC
        """, (patient_id,))
        records = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()
    return render_template("patient_dashboard.html", patient=patient,
                           total_records=len(records), records=records)


@app.route("/records")
@login_required
def records():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        if session["role"] == "doctor":
            cursor.execute("""
                SELECT mr.record_id, mr.patient_id, p.name AS patient_name,
                       mr.diagnosis, mr.prescription, mr.doctor_name,
                       mr.record_hash, mr.transaction_hash, mr.created_at
                FROM medical_records mr
                JOIN patients p ON p.patient_id=mr.patient_id
                JOIN doctor_patient dp
                  ON dp.patient_id=mr.patient_id AND dp.doctor_id=mr.doctor_id
                WHERE mr.doctor_id=%s
                ORDER BY mr.record_id DESC
            """, (session["doctor_id"],))
        else:
            cursor.execute("""
                SELECT mr.record_id, mr.patient_id, p.name AS patient_name,
                       mr.diagnosis, mr.prescription, mr.doctor_name,
                       mr.record_hash, mr.transaction_hash, mr.created_at
                FROM medical_records mr
                JOIN patients p ON p.patient_id=mr.patient_id
                WHERE mr.patient_id=%s
                ORDER BY mr.record_id DESC
            """, (session["patient_id"],))
        all_records = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()
    return render_template("records.html", records=all_records)


@app.route("/verify/<int:record_id>")
@login_required
def verify_record(record_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT mr.record_id, mr.patient_id, mr.doctor_id,
                   mr.diagnosis, mr.prescription, mr.doctor_name,
                   mr.record_hash, mr.transaction_hash, mr.created_at,
                   p.name AS patient_name
            FROM medical_records mr
            JOIN patients p ON p.patient_id=mr.patient_id
            WHERE mr.record_id=%s
        """, (record_id,))
        record = cursor.fetchone()
        if not record:
            flash("Record not found.", "error")
            return redirect(url_for("records"))

        if session["role"] == "patient":
            allowed = record["patient_id"] == session["patient_id"]
        else:
            cursor.execute("""
                SELECT assignment_id FROM doctor_patient
                WHERE doctor_id=%s AND patient_id=%s
            """, (session["doctor_id"], record["patient_id"]))
            currently_assigned = cursor.fetchone() is not None
            allowed = (
                record["doctor_id"] == session["doctor_id"]
                and currently_assigned
            )
    finally:
        cursor.close()
        connection.close()

    if not allowed:
        flash("You are not authorized to view or verify this record.", "error")
        return redirect(url_for("dashboard"))

    if not record["record_hash"]:
        return render_template("verify_result.html", record=record, verified=False,
                               db_matches=False, chain_matches=False, current_hash=None)
    record_data = {
        "record_id": int(record["record_id"]),
        "patient_id": int(record["patient_id"]),
        "diagnosis": record["diagnosis"],
        "prescription": record["prescription"] or "",
        "doctor_name": record["doctor_name"] or "",
    }
    try:
        current_hash = calculate_record_hash(record_data)
        db_matches = current_hash == record["record_hash"]
        chain_matches = verify_hash_on_blockchain(record_id, current_hash)
        return render_template("verify_result.html", record=record,
                               verified=db_matches and chain_matches,
                               db_matches=db_matches, chain_matches=chain_matches,
                               current_hash=current_hash)
    except Exception as exc:
        flash("Blockchain verification error: " + str(exc), "error")
        return redirect(url_for("records"))


if __name__ == "__main__":
    app.run(debug=True)
