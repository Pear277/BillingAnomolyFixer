import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def validate_and_suggest(row: pd.Series) -> pd.Series:
    issues = []
    corrections = {}

    # checks for difference in fresh/waste water usage
    if row["fresh_water_usage"] != row["waste_water_usage"]:
        issues.append("Fresh/Waste water usage mismatch")

    # Calculate actual expected charge
    expected_charge = round(
        row["fresh_water_usage"] * row["fresh_water_rate"] +
        row["waste_water_usage"] * row["waste_water_rate"] +
        row["fresh_water_fixed_charge"] +
        row["waste_water_fixed_charge"]
    , 2)

    if expected_charge != row["latest_charges"]:
        issues.append("Charge mismatch")
        corrections["expected_charges"] = round(expected_charge, 2)

        # if incorrect charge and usage mismatch
        if "Fresh/Waste water usage mismatch" in issues:
            corrections["note"] = "Price likely incorrect due to usage mismatch"

    # returns thef flagged issues        
    return pd.Series({
        "account_number": row.get("account_number", None),
        "bill_date": row.get("bill_date", None),
        "issues": issues,
        "corrections": corrections,
        "has_issues": len(issues) > 0

    })

def rule_based_check(df: pd.DataFrame) -> pd.DataFrame:
    # Apply validation function to each row
    results = df.apply(validate_and_suggest, axis=1)

    # Filter rows which need attention
    flagged = results[results['has_issues']]
    flagged = flagged.drop(columns=['has_issues'])
    return flagged

def ml_based_check(csv_path: str) -> pd.DataFrame:

    # Load and clean data
    df = pd.read_csv(csv_path)
    df['fresh_water_usage'] = pd.to_numeric(df['fresh_water_usage'], errors='coerce')
    df['waste_water_usage'] = pd.to_numeric(df['waste_water_usage'], errors='coerce')
    df['latest_charges'] = pd.to_numeric(df['latest_charges'], errors='coerce')
    df['number_of_bedrooms'] = pd.to_numeric(df.get('number_of_bedrooms', np.nan), errors='coerce')
    df['customer_id'] = df['account_number']
    df['total_water_usage'] = df['fresh_water_usage'] + df['waste_water_usage']
    core_features = ['total_water_usage', 'latest_charges']

    # Split customers by number of bills
    bill_counts = df.groupby('customer_id').size()
    high_customers = bill_counts[bill_counts >= 3].index
    low_customers = bill_counts[bill_counts < 3].index

    all_scored_rows = []

    ### 1. High-bill customers (analyze per customer)
    for cust_id in high_customers:
        cust_df = df[df['customer_id'] == cust_id].copy()
        if len(cust_df) < 3:
            continue

        X = cust_df[core_features]
        model = IsolationForest(n_estimators=100, contamination='auto', random_state=42)
        model.fit(X)
        scores = model.decision_function(X)
        cust_df['anomaly_score'] = scores
        all_scored_rows.append(cust_df)

    ### 2. Low-bill customers (clustered)
    df_low = df[df['customer_id'].isin(low_customers)].copy()
    if not df_low.empty:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df_low[core_features])
        kmeans = KMeans(n_clusters=3, random_state=42)
        df_low['cluster'] = kmeans.fit_predict(X_scaled)
        
        for cluster in df_low['cluster'].unique():
            cluster_df = df_low[df_low['cluster'] == cluster].copy()
            X_cluster = cluster_df[core_features]
            model = IsolationForest(n_estimators=100, contamination='auto', random_state=42)
            model.fit(X_cluster)
            scores = model.decision_function(X_cluster)
            cluster_df['anomaly_score'] = scores
            all_scored_rows.append(cluster_df)

    ### 3. Combine all scored data
    df_all = pd.concat(all_scored_rows, ignore_index=True)

    # Decide threshold — e.g., 3% are anomalies
    threshold = df_all['anomaly_score'].quantile(0.012)
    df_all['anomaly_flag'] = (df_all['anomaly_score'] < threshold).astype(int)
    anomalies = df_all[df_all['anomaly_flag'] == 1]

    cols = ["address","account_number","bill_date","billing_period_start","billing_period_end","fresh_water_usage","waste_water_usage","fresh_water_rate","fresh_water_fixed_charge","waste_water_rate","waste_water_fixed_charge","latest_charges"]

    anomalies = anomalies[cols]

    return anomalies