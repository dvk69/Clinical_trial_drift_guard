import sys
import time
from src.pipeline.generator import generate_synthetic_clinical_data
from src.pipeline.ingest import run_deidentification_pipeline
from src.analytics.drift_detector import run_site_drift_analysis

def main():
    print("===============================================================")
    print(" Starting Clinical Trial Data Integrity Pipeline")
    print(" Target Environment: DEDUCE / PACE Compatible Architecture")
    print("===============================================================\n")

    start_time = time.time()

    print("[Step 1/3] Generating synthetic multi-site clinical trial dataset...")
    generate_synthetic_clinical_data()

    print("\n[Step 2/3] Executing PySpark De-Identification Pipeline (Salted SHA-256)...")
    run_deidentification_pipeline()

    print("\n[Step 3/3] Running Kolmogorov-Smirnov & PSI Feature Drift Engine...")
    run_site_drift_analysis()

    elapsed = round(time.time() - start_time, 2)
    print("\n===============================================================")
    print(f" Pipeline Execution Successfully Finished in {elapsed} seconds!")
    print(" Launch UI Dashboard: `streamlit run src/dashboard/app.py` ")
    print("===============================================================")

if __name__ == "__main__":
    main()