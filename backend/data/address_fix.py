import pandas as pd
from rapidfuzz import fuzz

# Load your data
df = pd.read_csv('backend/data/cleaned_billing_data.csv')

# Ensure required column exists
assert 'address' in df.columns, "'address' column not found"

# Fuzzy clustering function
def get_most_common_fuzzy(addresses, threshold=90):
    clustered = []
    for addr in addresses:
        matched = False
        for group in clustered:
            if fuzz.ratio(addr, group[0]) > threshold:
                group.append(addr)
                matched = True
                break
        if not matched:
            clustered.append([addr])
    best_cluster = max(clustered, key=len)
    return max(set(best_cluster), key=best_cluster.count)

# Build correction map per customer
correction_map = {}
for acc_id, group in df.groupby('account_number'):
    addresses = group['address'].tolist()
    corrected = get_most_common_fuzzy(addresses)
    for addr in addresses:
        correction_map[(acc_id, addr)] = corrected

# Apply corrections and overwrite address column
df['address'] = df.apply(
    lambda row: correction_map.get((row['account_number'], row['address']), row['address']),
    axis=1
)

# Save updated file
df.to_csv('backend/data/cleaned_billing_data.csv', index=False)
