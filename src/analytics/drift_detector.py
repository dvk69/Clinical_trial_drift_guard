import pandas as pd
import numpy as np
from scipy.stats import ks_2samp
import json
import os
from src.utils.config import PROCESSED_DATA_PATH, DRIFT_REPORT_PATH

def calculate_psi(baseline, target, num_buckets=10):
    """Calculates Population Stability Index (PSI) between baseline and target distributions."""
    baseline = baseline[~np.isnan(baseline)]
    target = target[~np.isnan(target)]
    
    percentiles = np.linspace(0, 100, num_buckets + 1)
    buckets = np.percentile(baseline, percentiles)
    buckets[0] = -np.inf
    buckets[-1] = np.inf

    baseline_counts, _ = np.histogram(baseline, bins=buckets)
    target_counts, _ = np.histogram(target, bins=buckets)

    baseline_pct = baseline_counts / len(baseline)
    target_pct = target_counts / len(target)

    # Avoid zero division
    baseline_pct = np.where(baseline_pct == 0, 0.0001, baseline_pct)
    target_pct = np.where(target_pct == 0, 0.0001, target_pct)

    psi_val = np.sum((target_pct - baseline_pct) * np.log(target_pct / baseline_pct))
    return float(psi_val)

def run_site_drift_analysis():
    if not os.path.exists(PROCESSED_DATA_PATH):
        raise FileNotFoundError("De-identified parquet dataset missing.")

    df = pd.read_parquet(PROCESSED_DATA_PATH)
    
    # Baseline control site: SITE_001
    baseline_df = df[df["site_id"] == "SITE_001"]
    sites = sorted(df["site_id"].unique())
    metrics = []

    numerical_features = ["systolic_bp", "diastolic_bp", "serum_creatinine"]

    for site in sites:
        site_df = df[df["site_id"] == site]
        site_metrics = {"site_id": site, "features": {}}

        for feat in numerical_features:
            base_vals = baseline_df[feat].dropna().values
            curr_vals = site_df[feat].dropna().values

            # Two-sample Kolmogorov-Smirnov Test
            ks_stat, p_value = ks_2samp(base_vals, curr_vals)
            psi = calculate_psi(base_vals, curr_vals)

            drift_detected = bool(p_value < 0.01 and psi > 0.1)

            site_metrics["features"][feat] = {
                "ks_stat": round(float(ks_stat), 4),
                "p_value": float(p_value),
                "psi": round(psi, 4),
                "drift_detected": drift_detected,
                "mean": round(float(curr_vals.mean()), 2),
                "std": round(float(curr_vals.std()), 2)
            }

        metrics.append(site_metrics)

    with open(DRIFT_REPORT_PATH, "w") as f:
        json.dump(metrics, f, indent=4)

    print(f"[SUCCESS] Multi-site feature drift statistical analysis completed -> {DRIFT_REPORT_PATH}")
    return metrics

if __name__ == "__main__":
    run_site_drift_analysis()