import pandas as pd
import os
import csv
from rapidfuzz import fuzz

class BillingDataFixer:
    def __init__(self, threshold=90):
        self.threshold = threshold

    def robust_parse_date(self, val):
        dt = pd.to_datetime(val, errors='coerce', dayfirst=True)
        if pd.isnull(dt):
            dt = pd.to_datetime(val, errors='coerce', dayfirst=False)
        return '' if pd.isnull(dt) else dt.strftime('%d-%m-%Y')

    def load_valid_streets(self, folder_path):
        valid_streets = set()
        for filename in os.listdir(folder_path):
            if filename.endswith('.csv'):
                path = os.path.join(folder_path, filename)
                with open(path, newline='', encoding='utf-8-sig') as f:
                    reader = csv.reader(f)
                    for i, row in enumerate(reader):
                        # Skip header row (assumed first row)
                        if i == 0:
                            continue
                        if len(row) >= 3:
                            street = row[2].strip()  # third column is index 2
                            if street and street.lower() != "sea" and len(street) > 2:
                                valid_streets.add(street)
        print(f"Loaded {len(valid_streets)} valid street names.")
        return valid_streets

    def cluster_streets(self, streets):
        clustered = []
        for street in streets:
            matched = False
            for group in clustered:
                if fuzz.ratio(street, group[0]) > self.threshold:
                    group.append(street)
                    matched = True
                    break
            if not matched:
                clustered.append([street])
        return clustered

    def get_best_variant(self, cluster, reference):
        freq = pd.Series(cluster).value_counts()
        for candidate in freq.index:
            if candidate in reference:
                return candidate
        return freq.idxmax()

    def run(self, billing_path: str,reference_folder: str, output_path: str) -> str:
        df = pd.read_csv(billing_path)

        # Clean strings
        df = df.drop_duplicates()
        str_cols = df.select_dtypes(include='object').columns
        for col in str_cols:
            df[col] = df[col].astype(str).str.strip()

        # Standardize dates
        for col in ['bill_date', 'billing_period_start', 'billing_period_end']:
            if col in df.columns:
                df[col] = df[col].apply(self.robust_parse_date)

        # Fix numeric types
        numeric_cols = ['fresh_water_rate', 'fresh_water_fixed_charge', 'waste_water_rate',
                        'waste_water_fixed_charge', 'latest_charges']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').round(2)

        # Street corrections
        df["street"] = df["address"].apply(lambda x: x.split(",")[0].strip())
        valid_streets = self.load_valid_streets(reference_folder)

        correction_map = {}
        for acc_id, group in df.groupby("account_number"):
            streets = group["street"].tolist()
            clusters = self.cluster_streets(streets)
            best = self.get_best_variant(sum(clusters, []), valid_streets)
            for street in streets:
                correction_map[(acc_id, street)] = best

        df["corrected_street"] = df.apply(
            lambda row: correction_map.get((row["account_number"], row["street"]), row["street"]),
            axis=1
        )

        df["address"] = df.apply(
            lambda row: ', '.join([row["corrected_street"]] + [part.strip() for part in row["address"].split(',')[1:]]),
            axis=1
        )

        df.drop(columns=["street", "corrected_street"], inplace=True)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        return output_path