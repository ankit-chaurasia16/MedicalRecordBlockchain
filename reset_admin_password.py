from getpass import getpass
from werkzeug.security import generate_password_hash
from database import get_connection

email = "admin@medicalchain.local"

password = getpass("Enter new admin password (minimum 12 characters): ")
confirm = getpass("Confirm new password: ")

if len(password) < 12:
    raise SystemExit("Password must contain at least 12 characters.")

if password != confirm:
    raise SystemExit("Passwords do not match.")

connection = get_connection()
cursor = connection.cursor()

try:
    cursor.execute(
        "UPDATE users SET password_hash = %s WHERE email = %s AND role = 'admin'",
        (generate_password_hash(password), email)
    )

    if cursor.rowcount != 1:
        connection.rollback()
        raise SystemExit("Admin account not found or update failed.")

    connection.commit()
    print("Admin password updated successfully.")

finally:
    cursor.close()
    connection.close()
