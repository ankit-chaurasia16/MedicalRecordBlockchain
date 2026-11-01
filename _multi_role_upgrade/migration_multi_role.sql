-- MedicalChain multi-role + approval migration
-- BACK UP the database before running this file. Run once against medical_blockchain.

-- Keep existing doctor and patient users valid, and add the new account roles.
ALTER TABLE users
  MODIFY COLUMN role ENUM(
    'doctor', 'nurse', 'pharmacist', 'lab_technician',
    'physiotherapist', 'patient', 'admin'
  ) NOT NULL;

-- Existing accounts become approved by default; new professional registrations are pending.
ALTER TABLE users
  ADD COLUMN account_status ENUM('pending', 'approved', 'rejected')
  NOT NULL DEFAULT 'approved' AFTER role;

CREATE TABLE healthcare_professionals (
  professional_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL UNIQUE,
  full_name VARCHAR(100) NOT NULL,
  professional_type ENUM('nurse', 'pharmacist', 'lab_technician', 'physiotherapist') NOT NULL,
  qualification VARCHAR(100) NOT NULL,
  department VARCHAR(100) NOT NULL,
  specialization VARCHAR(100) NULL,
  registration_number VARCHAR(100) NOT NULL UNIQUE,
  years_experience INT NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_healthcare_professional_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Non-doctor professionals only receive access to patients assigned by an administrator.
CREATE TABLE care_team_assignments (
  assignment_id INT AUTO_INCREMENT PRIMARY KEY,
  professional_id INT NOT NULL,
  patient_id INT NOT NULL,
  assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_professional_patient (professional_id, patient_id),
  KEY idx_care_team_patient (patient_id),
  CONSTRAINT fk_care_team_professional
    FOREIGN KEY (professional_id) REFERENCES healthcare_professionals(professional_id) ON DELETE CASCADE,
  CONSTRAINT fk_care_team_patient
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- These are role-specific work notes, not physician diagnoses or prescriptions.
CREATE TABLE professional_notes (
  note_id INT AUTO_INCREMENT PRIMARY KEY,
  professional_id INT NOT NULL,
  patient_id INT NOT NULL,
  note_type ENUM('nurse', 'pharmacist', 'lab_technician', 'physiotherapist') NOT NULL,
  details TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  KEY idx_professional_notes_patient (patient_id),
  KEY idx_professional_notes_professional (professional_id),
  CONSTRAINT fk_professional_notes_professional
    FOREIGN KEY (professional_id) REFERENCES healthcare_professionals(professional_id) ON DELETE CASCADE,
  CONSTRAINT fk_professional_notes_patient
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Review the result after migration. Existing rows should remain approved.
SELECT role, account_status, COUNT(*) AS total_users
FROM users
GROUP BY role, account_status
ORDER BY role, account_status;
