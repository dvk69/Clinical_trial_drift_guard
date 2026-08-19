import pandas as pd
import numpy as np
from faker import Faker
import os
from src.utils.config import RAW_DATA_PATH, NUM_SITES, NUM_PATIENTS_PER_SITE

def generate_synthetic_clinical_data():
    fake = Faker()
    Faker.seed(42)
    np.random.seed(42)

    records = []
    
    for site_id in range(1, NUM_SITES + 1):
        # Inject systematic calibration drift in Sites 4 & 5
        bp_mean_shift = 0.0 if site_id <= 3 else 22.5  
        lab_error_rate = 0.02 if site_id <= 3 else 0.15 

        for _ in range(NUM_PATIENTS_PER_SITE):
            patient_name = fake.name()
            ssn = fake.ssn()
            dob = fake.date_of_birth(minimum_age=18, maximum_age=85).strftime("%Y-%m-%d")
            patient_id = f"PAT-{fake.unique.random_number(digits=6)}"
            
            # Normal Systolic BP distribution ~ N(120, 10), plus site calibration drift
            systolic_bp = float(np.random.normal(120 + bp_mean_shift, 10))
            diastolic_bp = float(np.random.normal(80 + (bp_mean_shift * 0.5), 8))
            
            # Lab measurement (e.g., serum creatinine in mg/dL)
            creatinine = float(np.random.normal(1.0, 0.2))
            if np.random.rand() < lab_error_rate:
                creatinine = creatinine * 5.0 # Sensor outlier artifact

            records.append({
                "site_id": f"SITE_00{site_id}",
                "patient_id": patient_id,
                "patient_name": patient_name,
                "ssn": ssn,
                "dob": dob,
                "systolic_bp": round(systolic_bp, 2),
                "diastolic_bp": round(diastolic_bp, 2),
                "serum_creatinine": round(creatinine, 2),
                "trial_arm": np.random.choice(["Control", "Treatment_A", "Treatment_B"]),
                "ingestion_timestamp": fake.date_time_this_year().strftime("%Y-%m-%d %H:%M:%S")
            })

    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
    df.to_csv(RAW_DATA_PATH, index=False)
    print(f"[SUCCESS] Synthetic trial dataset generated: {len(df)} records -> {RAW_DATA_PATH}")

if __name__ == "__main__":
    generate_synthetic_clinical_data()