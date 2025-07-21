import pandas as pd
import os
import csv
from rapidfuzz import fuzz

def clean_and_fix_billing_data(
    billing_path: str,
    reference_folder: str,
    output_path: str,
    date_columns=['bill_date', 'billing_period_start', 'billing_period_end'],
    threshold=90
) -> str:

    # Step 1 – Load billing data
    df = pd.read_csv(billing_path)

    # Step 2 – Clean dates
    def robust_parse_date(val):
        dt = pd.to_datetime(val, errors='coerce', dayfirst=True)
        if pd.isnull(dt):
            dt = pd.to_datetime(val, errors='coerce', dayfirst=False)
        return '' if pd.isnull(dt) else dt.strftime('%d-%m-%Y')

    for col in date_columns:
        if col in df.columns:
            df[col] = df[col].apply(robust_parse_date)

    # Step 3 – Clean numerics
    float_cols = ['fresh_water_rate', 'fresh_water_fixed_charge', 'waste_water_rate', 'waste_water_fixed_charge', 'latest_charges']
    for col in float_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').round(2)

    # Step 4 – Trim strings & remove duplicates
    str_cols = df.select_dtypes(include=['object']).columns
    for col in str_cols:
        df[col] = df[col].str.strip()
    df.drop_duplicates(inplace=True)

    # Step 5 – Extract streets from addresses
    df['street'] = df['address'].apply(lambda x: x.split(',')[0].strip())

    # Step 6 – Load reference streets
    def load_valid_streets(folder_path):
        valid_streets = set()
        for filename in os.listdir(folder_path):
            if filename.endswith('.csv'):
                with open(os.path.join(folder_path, filename), newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        street = row.get("name1")
                        if street:
                            valid_streets.add(street.strip())
        return valid_streets

    valid_streets = load_valid_streets(reference_folder)

    # Step 7 – Fuzzy cluster street names
    def cluster_streets(streets):
        clustered = []
        for street in streets:
            matched = False
            for group in clustered:
                if fuzz.ratio(street, group[0]) > threshold:
                    group.append(street)
                    matched = True
                    break
            if not matched:
                clustered.append([street])
        return clustered

    def get_best_variant(cluster, reference):
        freq = pd.Series(cluster).value_counts()
        for candidate in freq.index:
            if candidate in reference:
                return candidate
        return freq.idxmax()

    street_map = {}
    for acc_id, group in df.groupby("account_number"):
        streets = group["street"].tolist()
        clusters = cluster_streets(streets)
        best = get_best_variant(sum(clusters, []), valid_streets)
        for street in streets:
            street_map[(acc_id, street)] = best

    # Step 8 – Apply corrections
    df['corrected_street'] = df.apply(
        lambda row: street_map.get((row['account_number'], row['street']), row['street']),
        axis=1
    )

    def rebuild_address(original, corrected):
        parts = original.split(',')
        parts[0] = corrected
        return ', '.join(part.strip() for part in parts)

    df['address'] = df.apply(
        lambda row: rebuild_address(row['address'], row['corrected_street']),
        axis=1
    )

    # Final cleanup
    df.drop(columns=['street', 'corrected_street'], inplace=True)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    return f"✅ Data cleaned and fixed. Output saved to: {output_path}"
