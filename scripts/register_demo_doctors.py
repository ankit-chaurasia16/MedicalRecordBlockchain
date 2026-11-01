"""Register demo doctors by submitting the actual Flask doctor-registration route.

Run from the project root:
    python scripts/register_demo_doctors.py

Existing accounts are not duplicated. The script does not insert doctors with SQL.
Demo password for newly created accounts: Demo@12345
"""
from app import app, assign_existing_unassigned_patients

DEMO_PASSWORD = "Demo@12345"

# Four General Medicine doctors total including existing Dr. Amit Kumar.
# Three other General Medicine accounts + four doctors in each other department = 36 total.
doctors = [
    ("Dr. Neha Gupta", "demo.neha@medicalchain.demo", "MBBS, MD (General Medicine)", "General Medicine", "General Medicine", "DEMO-GM-002", 9),
    ("Dr. Raj Malhotra", "demo.raj@medicalchain.demo", "MBBS, MD (General Medicine)", "General Medicine", "General Medicine", "DEMO-GM-003", 11),
    ("Dr. Sana Kapoor", "demo.sana@medicalchain.demo", "MBBS, MD (General Medicine)", "General Medicine", "General Medicine", "DEMO-GM-004", 7),

    ("Dr. Kavita Sharma", "demo.kavita.cardio@medicalchain.demo", "MBBS, MD (Cardiology)", "Cardiology", "Cardiology", "DEMO-CA-001", 10),
    ("Dr. Rohan Mehta", "demo.rohan.cardio@medicalchain.demo", "MBBS, DM (Cardiology)", "Cardiology", "Cardiology", "DEMO-CA-002", 12),
    ("Dr. Meera Sethi", "demo.meera.cardio@medicalchain.demo", "MBBS, MD (Medicine), DM (Cardiology)", "Cardiology", "Cardiology", "DEMO-CA-003", 8),
    ("Dr. Arvind Rao", "demo.arvind.cardio@medicalchain.demo", "MBBS, MD (Cardiology)", "Cardiology", "Cardiology", "DEMO-CA-004", 6),

    ("Dr. Pooja Verma", "demo.pooja.derm@medicalchain.demo", "MBBS, MD (Dermatology)", "Dermatology", "Dermatology", "DEMO-DE-001", 8),
    ("Dr. Nisha Bansal", "demo.nisha.derm@medicalchain.demo", "MBBS, MD (Dermatology)", "Dermatology", "Dermatology", "DEMO-DE-002", 5),
    ("Dr. Karan Arora", "demo.karan.derm@medicalchain.demo", "MBBS, MD (Dermatology)", "Dermatology", "Dermatology", "DEMO-DE-003", 7),
    ("Dr. Simran Gill", "demo.simran.derm@medicalchain.demo", "MBBS, DVD", "Dermatology", "Dermatology", "DEMO-DE-004", 4),

    ("Dr. Vivek Khanna", "demo.vivek.neuro@medicalchain.demo", "MBBS, MD, DM (Neurology)", "Neurology", "Neurology", "DEMO-NE-001", 13),
    ("Dr. Aditi Rao", "demo.aditi.neuro@medicalchain.demo", "MBBS, MD (Medicine), DM (Neurology)", "Neurology", "Neurology", "DEMO-NE-002", 9),
    ("Dr. Manish Sood", "demo.manish.neuro@medicalchain.demo", "MBBS, MD, DM (Neurology)", "Neurology", "Neurology", "DEMO-NE-003", 7),
    ("Dr. Isha Nair", "demo.isha.neuro@medicalchain.demo", "MBBS, DM (Neurology)", "Neurology", "Neurology", "DEMO-NE-004", 6),

    ("Dr. Pooja Verma Ortho", "demo.pooja.ortho@medicalchain.demo", "MBBS, MS (Orthopedics)", "Orthopedics", "Orthopedics", "DEMO-OR-001", 9),
    ("Dr. Aman Suri", "demo.aman.ortho@medicalchain.demo", "MBBS, MS (Orthopedics)", "Orthopedics", "Orthopedics", "DEMO-OR-002", 8),
    ("Dr. Deepak Jain", "demo.deepak.ortho@medicalchain.demo", "MBBS, MS (Orthopedics)", "Orthopedics", "Orthopedics", "DEMO-OR-003", 11),
    ("Dr. Ritu Malhotra", "demo.ritu.ortho@medicalchain.demo", "MBBS, DNB (Orthopedics)", "Orthopedics", "Orthopedics", "DEMO-OR-004", 5),

    ("Dr. Alka Menon", "demo.alka.pedia@medicalchain.demo", "MBBS, MD (Pediatrics)", "Pediatrics", "Pediatrics", "DEMO-PE-001", 10),
    ("Dr. Saurabh Bedi", "demo.saurabh.pedia@medicalchain.demo", "MBBS, MD (Pediatrics)", "Pediatrics", "Pediatrics", "DEMO-PE-002", 8),
    ("Dr. Neelam Das", "demo.neelam.pedia@medicalchain.demo", "MBBS, DCH", "Pediatrics", "Pediatrics", "DEMO-PE-003", 6),
    ("Dr. Harsh Vardhan", "demo.harsh.pedia@medicalchain.demo", "MBBS, MD (Pediatrics)", "Pediatrics", "Pediatrics", "DEMO-PE-004", 7),

    ("Dr. Rhea Kapoor", "demo.rhea.eye@medicalchain.demo", "MBBS, MS (Ophthalmology)", "Ophthalmology", "Ophthalmology", "DEMO-OP-001", 8),
    ("Dr. Nitin Shah", "demo.nitin.eye@medicalchain.demo", "MBBS, MS (Ophthalmology)", "Ophthalmology", "Ophthalmology", "DEMO-OP-002", 10),
    ("Dr. Charu Bhatia", "demo.charu.eye@medicalchain.demo", "MBBS, DOMS", "Ophthalmology", "Ophthalmology", "DEMO-OP-003", 5),
    ("Dr. Mohit Anand", "demo.mohit.eye@medicalchain.demo", "MBBS, MS (Ophthalmology)", "Ophthalmology", "Ophthalmology", "DEMO-OP-004", 6),

    ("Dr. Shalini Rao", "demo.shalini.gyn@medicalchain.demo", "MBBS, MS (Obstetrics and Gynecology)", "Gynecology", "Gynecology", "DEMO-GY-001", 12),
    ("Dr. Nupur Khanna", "demo.nupur.gyn@medicalchain.demo", "MBBS, MD (Obstetrics and Gynecology)", "Gynecology", "Gynecology", "DEMO-GY-002", 9),
    ("Dr. Farah Ali", "demo.farah.gyn@medicalchain.demo", "MBBS, DGO", "Gynecology", "Gynecology", "DEMO-GY-003", 7),
    ("Dr. Tanya Sood", "demo.tanya.gyn@medicalchain.demo", "MBBS, MS (Obstetrics and Gynecology)", "Gynecology", "Gynecology", "DEMO-GY-004", 5),

    ("Dr. Kabir Anand", "demo.kabir.psych@medicalchain.demo", "MBBS, MD (Psychiatry)", "Psychiatry", "Psychiatry", "DEMO-PS-001", 10),
    ("Dr. Radhika Sen", "demo.radhika.psych@medicalchain.demo", "MBBS, MD (Psychiatry)", "Psychiatry", "Psychiatry", "DEMO-PS-002", 8),
    ("Dr. Sameer Paul", "demo.sameer.psych@medicalchain.demo", "MBBS, DPM", "Psychiatry", "Psychiatry", "DEMO-PS-003", 6),
    ("Dr. Leena Joseph", "demo.leena.psych@medicalchain.demo", "MBBS, MD (Psychiatry)", "Psychiatry", "Psychiatry", "DEMO-PS-004", 7),
]

def main():
    app.config["TESTING"] = True
    created = 0
    skipped = 0
    with app.test_client() as client:
        for name, email, qualification, specialization, department, license_no, experience in doctors:
            response = client.post("/register/doctor", data={
                "name": name,
                "email": email,
                "password": DEMO_PASSWORD,
                "qualification": qualification,
                "specialization": specialization,
                "department": department,
                "license_number": license_no,
                "years_experience": str(experience),
            }, follow_redirects=False)
            if response.status_code in (302, 303):
                created += 1
                print(f"REGISTERED: {email}")
            else:
                # The route's duplicate validation returns the form with HTTP 200.
                skipped += 1
                print(f"CHECK/SKIP: {email} (HTTP {response.status_code}; may already exist or require validation)")
    print(f"\nRegistration requests completed. New/redirected: {created}; checked/skipped: {skipped}")
    print(f"Demo password for these demo accounts: {DEMO_PASSWORD}")
    print("\nNow assigning existing patients who currently have no doctor...")
    try:
        assigned = assign_existing_unassigned_patients()
        if assigned:
            for patient_id, doctor_id in assigned:
                print(f"Patient ID {patient_id} assigned to Doctor ID {doctor_id}")
        else:
            print("No unassigned patients found.")
    except Exception as exc:
        print("Assignment did not complete:", exc)
        print("Check patient disease_category values and doctor departments.")

if __name__ == "__main__":
    main()
