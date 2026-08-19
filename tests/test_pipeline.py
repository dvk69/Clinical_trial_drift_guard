import pytest
import pandas as pd
import os
from src.utils.config import PROCESSED_DATA_PATH, RAW_DATA_PATH
from src.pipeline.generator import generate_synthetic_clinical_data
from src.pipeline.ingest import run_deidentification_pipeline

def test_pipeline_execution():
    generate_synthetic_clinical_data()
    assert os.path.exists(RAW_DATA_PATH)

    df_processed = run_deidentification_pipeline()
    assert os.path.exists(PROCESSED_DATA_PATH)

    # Convert Spark DF to Pandas for assertion checks
    pdf = pd.read_parquet(PROCESSED_DATA_PATH)
    
    # Security Rule 1: No direct PII column leakage
    assert "ssn" not in pdf.columns
    assert "patient_name" not in pdf.columns
    assert "patient_id" not in pdf.columns
    
    # Security Rule 2: Masked Patient ID exists
    assert "masked_patient_id" in pdf.columns
    assert pdf["masked_patient_id"].nunique() > 0