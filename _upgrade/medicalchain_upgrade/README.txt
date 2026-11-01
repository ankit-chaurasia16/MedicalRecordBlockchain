# MedicalChain upgrade

## Before replacing files
1. Stop Flask with Ctrl+C.
2. Back up your current `app.py` and the entire `templates` folder.
3. Keep `database.py`, `blockchain.py`, `deployed_contract.json`, `contracts/`, `hardhat.config.ts`, and MySQL data unchanged.

## Install
Copy `app.py` to the project root. Copy the supplied `templates` folder into your project `templates` folder, replacing same-named templates.

The database columns shown in your latest output are compatible with this app:
- doctors.department, qualification, years_experience
- patients.disease_category
- doctor_patient.status
- medical_records.doctor_id

## Run
1. Keep the Hardhat node running in its separate terminal.
2. From project root with venv activated:
   `python -m py_compile app.py`
   `python app.py`
3. Open `http://127.0.0.1:5000/register/doctor` to register doctors manually.

## Register demo doctors
Stop Flask first, then from project root run:
`python scripts/register_demo_doctors.py`

This script submits POST requests to the real Flask `/register/doctor` route using Flask's test client. It does not insert doctor rows with direct SQL. Existing patients with no assignment are then assigned using the same least-pending-workload helper used by patient registration.

All demo accounts use password `Demo@12345`. Demo doctor names, qualifications and license numbers are fictional and are not evidence of real professional credentials.

## Security and limitations
- This is an academic local demo, not a production medical system.
- Doctor self-registration does not verify a real medical license; real deployment needs admin approval and credential validation.
- Patient category selects a department for routing; it is not a clinical diagnosis.
- Medical record ownership is stored in MySQL via doctor_id. The blockchain stores the record-content hash, not patient medical details.
