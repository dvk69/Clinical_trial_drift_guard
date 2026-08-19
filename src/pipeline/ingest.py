from pyspark.sql import SparkSession
from pyspark.sql.functions import col, concat_ws, sha2, lit, regexp_replace
import os
from src.utils.config import RAW_DATA_PATH, PROCESSED_DATA_PATH, HASH_SALT

def get_spark_session():
    return SparkSession.builder \
        .appName("Duke_Clinical_Trial_DeIdentification_Pipeline") \
        .master("local[*]") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()

def run_deidentification_pipeline():
    spark = get_spark_session()
    
    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(f"Raw data file not found at {RAW_DATA_PATH}. Run generator first.")

    # Read raw multi-site trial data
    raw_df = spark.read.option("header", "true").csv(RAW_DATA_PATH)

    # De-Identification Layer: Salted SHA-256 for Patient Identifiers
    deidentified_df = raw_df \
        .withColumn("salted_id_input", concat_ws("_", col("patient_id"), col("ssn"), lit(HASH_SALT))) \
        .withColumn("masked_patient_id", sha2(col("salted_id_input"), 256)) \
        .drop("patient_name", "ssn", "patient_id", "salted_id_input")

    # Cast numeric attributes for biostatistical compute
    typed_df = deidentified_df \
        .withColumn("systolic_bp", col("systolic_bp").cast("double")) \
        .withColumn("diastolic_bp", col("diastolic_bp").cast("double")) \
        .withColumn("serum_creatinine", col("serum_creatinine").cast("double"))

    # Export sanitized output to Parquet
    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    typed_df.write.mode("overwrite").parquet(PROCESSED_DATA_PATH)
    
    print(f"[SUCCESS] PySpark de-identification pipeline executed. Clean dataset written to {PROCESSED_DATA_PATH}")
    return typed_df

if __name__ == "__main__":
    run_deidentification_pipeline()