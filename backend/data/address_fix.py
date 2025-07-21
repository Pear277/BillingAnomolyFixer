import pandas as pd
from rapidfuzz import fuzz
import os 
import csv

# Paths
billing_data_path = 'backend/data/cleaned_billing_data2.csv'
street_reference_path = 'backend/data/opname_csv_gb'
output_path = 'backend/data/cleaned_billing_streetfix.csv'

# load data
df_original = pd.read_csv(billing_data_path)
df = df_original.copy()

# Threshold for fuzzy matching
threshold = 90

df['street'] = df['address'].apply(lambda x: x.split(',')[0].strip())

# Load UK reference street names from OS Open Names
def load_valid_streets(folder_path):
    valid_streets = set()
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            full_path = os.path.join(folder_path, filename)
            with open(full_path, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    street = row.get("name1")
                    if street:
                        valid_streets.add(street.strip())
    return valid_streets

valid_streets = load_valid_streets(street_reference_path)


# Ensure required column exists
assert 'address' in df.columns, "'address' column not found"

# Fuzzy clustering
def cluster_streets(streets, threshold=90):
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

# Select best variant from cluster
def get_best_variant(cluster, reference):
    freq = pd.Series(cluster).value_counts()
    # Prefer variant found in reference street names
    for candidate in freq.index:
        if candidate in reference:
            return candidate
    return freq.idxmax()

# Build correction map
street_correction_map = {}
for acc_id, group in df.groupby('account_number'):
    streets = group['street'].tolist()
    clusters = cluster_streets(streets, threshold=threshold)
    best = get_best_variant(sum(clusters, []), valid_streets)
    for street in streets:
        street_correction_map[(acc_id, street)] = best

# Apply corrections
df_corrected = df.copy()
df_corrected['corrected_street'] = df_corrected.apply(
    lambda row: street_correction_map.get((row['account_number'], row['street']), row['street']),
    axis=1
)
# Replace only the street part of the address
def rebuild_address(original_address, corrected_street):
    parts = original_address.split(',')
    parts[0] = corrected_street
    return ", ".join(part.strip() for part in parts)

df_corrected['address'] = df_corrected.apply(
    lambda row: rebuild_address(row['address'], row['corrected_street']),
    axis=1
)

# Clean up
df_corrected.drop(columns=['street', 'corrected_street'], inplace=True)
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df_corrected.to_csv(output_path, index=False)

