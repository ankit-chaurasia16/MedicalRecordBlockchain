# MedicalChain Multi-Role Upgrade

This upgrade adds separate portals for doctors, nurses, pharmacists, laboratory technicians, physiotherapists, patients, and an administrator. New professional accounts are **pending** until an administrator approves or rejects them. Existing doctor and patient accounts are preserved as approved by the database migration default.

## Important limitations

- This is an academic demonstration, not a production clinical system.
- The app collects qualification and registration numbers but does not verify them with a regulator.
- Do not enter real patient information.
- The administrator must verify documents outside this demo before approving an account.
- Doctor diagnoses and prescriptions remain doctor-only. Other professionals can only create their own role-specific notes for patients assigned to them.
- Pharmacists receive read-only prescription information for assigned patients. Lab technicians see patient identifiers and can create workflow notes; this version does not implement lab orders or validated result reporting.

## 1. Back up your database first

In PowerShell, open MySQL:

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe" -u root -p medical_blockchain > medical_blockchain_before_multi_role.sql
```

Keep the backup outside the project folder too.

## 2. Apply the database migration once

Open MySQL from the project folder:

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p medical_blockchain
```

At the `mysql>` prompt, run:

```sql
source migration_multi_role.sql;
```

The SQL file is a **one-time migration**; do not run it twice because it adds a column and creates tables. If MySQL says it cannot find the file, use the full path with forward slashes, for example `source C:/Users/ankit/MedicalRecordBlockchain/migration_multi_role.sql;`.

## 3. Create the administrator account

Activate your existing virtual environment and go to the project folder. Set a unique admin email and a strong password in PowerShell:

```powershell
$env:ADMIN_EMAIL = "admin@medicalchain.local"
$env:ADMIN_PASSWORD = "Replace-With-A-Unique-Password-At-Least-12-Chars"
python create_admin.py
```

Do not share this password. The script stores only a password hash.

## 4. Install / run

No new Python package is required beyond the existing requirements. Start your Hardhat node as before if you need blockchain verification, then start Flask on the known working port:

```powershell
python -c "import app; app.app.config['TEMPLATES_AUTO_RELOAD']=True; app.app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)"
```

Open `http://127.0.0.1:5001/login`.

## 5. First-time workflow

1. Sign in to the Administrator portal with the account created in step 3.
2. Review pending doctor / nurse / pharmacist / lab technician / physiotherapist registrations.
3. Approve only after independently checking their credentials. Reject invalid submissions.
4. Assign approved non-doctor professionals to patients in the admin console.
5. Each professional can then sign in through their own portal and access only assigned patients.
6. Patients can view their own doctor records and professional care notes.

## Role permissions in this demo

| Role | Allowed actions |
|---|---|
| Doctor | View assigned patients; create diagnosis and prescription records; secure records on blockchain |
| Nurse | View assigned patient list; add nursing notes; no diagnosis or prescription creation |
| Pharmacist | View prescriptions for assigned patients; add dispensing / medication-review notes; no diagnosis or prescription editing |
| Lab technician | View assigned patient identifiers; add lab workflow notes; no diagnosis or prescription access |
| Physiotherapist | View assigned patient list; add physiotherapy progress notes; no diagnosis or prescription creation |
| Patient | View own medical records, verification results, and care-team notes |
| Admin | Approve/reject professional accounts and assign non-doctor professionals; no clinical record editing |

## Files added / changed

- `app.py`: role login, professional registration, approval, assignments, role-specific workspaces and notes.
- `templates/`: new admin and professional dashboards; updated login, navigation, and doctor qualification selection.
- `migration_multi_role.sql`: one-time schema migration.
- `create_admin.py`: creates the initial administrator from environment variables.
- `static/style.css`: responsive additions for the new screens.

The original `blockchain.py` and `database.py` are retained unchanged.
