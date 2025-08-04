import pandas as pd
import os
import csv
from rapidfuzz import fuzz
from .autofix_tracker import AutofixTracker

class BillingDataFixer:
    def __init__(self, threshold=90):
        self.threshold = threshold
        self.tracker = AutofixTracker()

    def robust_parse_date(self, val, account_number=None, bill_date=None, field=None):
        original = str(val)
        dt = pd.to_datetime(val, errors='coerce', dayfirst=True)
        if pd.isnull(dt):
            dt = pd.to_datetime(val, errors='coerce', dayfirst=False)
        
        fixed = '' if pd.isnull(dt) else dt.strftime('%d-%m-%Y')
        
        # Track change if values differ
        if original != fixed and account_number and field:
            self.tracker.track_date_fix(account_number, bill_date, field, original, fixed)
        
        return fixed

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

        # Standardize dates with tracking
        for col in ['bill_date', 'billing_period_start', 'billing_period_end']:
            if col in df.columns:
                df[col] = df.apply(lambda row: self.robust_parse_date(
                    row[col], 
                    row.get('account_number'), 
                    row.get('bill_date'), 
                    col
                ), axis=1)

        # Fix numeric types with tracking
        numeric_cols = ['fresh_water_rate', 'fresh_water_fixed_charge', 'waste_water_rate',
                        'waste_water_fixed_charge', 'latest_charges']
        for col in numeric_cols:
            if col in df.columns:
                original_values = df[col].astype(str)
                df[col] = pd.to_numeric(df[col], errors='coerce').round(2)
                
                # Track numeric changes
                for idx, (orig, fixed) in enumerate(zip(original_values, df[col])):
                    if str(orig) != str(fixed) and not pd.isna(fixed):
                        self.tracker.track_numeric_fix(
                            df.iloc[idx]['account_number'],
                            df.iloc[idx]['bill_date'],
                            col, orig, fixed
                        )

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

        # Track address changes and apply corrections
        def fix_address(row):
            original = row["address"]
            fixed = ', '.join([row["corrected_street"]] + [part.strip() for part in row["address"].split(',')[1:]])
            
            if original != fixed:
                self.tracker.track_address_fix(
                    row["account_number"],
                    row["bill_date"],
                    original,
                    fixed
                )
            return fixed
        
        df["address"] = df.apply(fix_address, axis=1)

        df.drop(columns=["street", "corrected_street"], inplace=True)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        
        # Save autofix changes log
        changes_path = output_path.replace('.csv', '_autofix_changes.json')
        changes_count = self.tracker.save_changes(changes_path)
        summary = self.tracker.get_summary()
        
        return f"Cleaned data saved to {output_path}. Made {changes_count} changes: {summary}. Changes log: {changes_path}"