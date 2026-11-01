"""Create the first MedicalChain administrator using environment variables.

PowerShell example:
  $env:ADMIN_EMAIL = "admin@medicalchain.local"
  $env:ADMIN_PASSWORD = "Use-A-Strong-Unique-Password"
  python create_admin.py
"""
import os
from werkzeug.security import generate_password_hash
from mysql.connector import IntegrityError
from database import get_connection

email = os.getenv("ADMIN_EMAIL", "").strip().lower()
password = os.getenv("ADMIN_PASSWORD", "")
if not email or len(password) < 12:
    raise SystemExit("Set ADMIN_EMAIL and ADMIN_PASSWORD (minimum 12 characters) in the environment first.")

connection = get_connection()
cursor = connection.cursor()
try:
    cursor.execute("""INSERT INTO users (email, password_hash, role, account_status)
                      VALUES (%s, %s, 'admin', 'approved')""",
                   (email, generate_password_hash(password)))
    connection.commit()
    print("Administrator account created:", email)
except IntegrityError:
    connection.rollback()
    raise SystemExit("That email already exists. Use a different ADMIN_EMAIL or check the existing account.")
finally:
    cursor.close()
    connection.close()
