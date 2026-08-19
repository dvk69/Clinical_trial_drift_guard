import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "clinical_trials_raw.csv")
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "deidentified_trials.parquet")
DRIFT_REPORT_PATH = os.path.join(BASE_DIR, "data", "processed", "drift_metrics.json")

# Salt key used for irreversible SHA-256 PII masking
HASH_SALT = "Duke_PACE_Secure_Salt_2026_Key"
NUM_SITES = 5
NUM_PATIENTS_PER_SITE = 2000