import csv
import random
import re

# Read the UK addresses
with open('uk_addresses.txt', 'r') as f:
    uk_addresses = [line.strip() for line in f.readlines()]

# Read the CSV file
with open('backend/data/mock_billing_data_updated.csv', 'r') as f:
    reader = csv.reader(f)
    rows = list(reader)

# Get unique addresses from the CSV
unique_addresses = set()
for row in rows[1:]:  # Skip header
    address = row[0].strip('"')
    unique_addresses.add(address)

# Create a mapping of old addresses to new addresses
address_mapping = {}
uk_addresses_copy = uk_addresses.copy()
random.shuffle(uk_addresses_copy)

for old_address in unique_addresses:
    if uk_addresses_copy:
        new_address = uk_addresses_copy.pop()
        address_mapping[old_address] = new_address
    else:
        # If we run out of UK addresses, generate variations
        base_address = random.choice(uk_addresses)
        parts = base_address.split(',')
        number = random.randint(1, 100)
        street = parts[0].split(' ', 1)[1]
        town = parts[1].strip()
        postcode = parts[2].strip()
        new_address = f"{number} {street}, {town}, {postcode}"
        address_mapping[old_address] = new_address

# Replace addresses in the CSV
for i in range(1, len(rows)):  # Skip header
    old_address = rows[i][0].strip('"')
    if old_address in address_mapping:
        rows[i][0] = f'"{address_mapping[old_address]}"'

# Write the updated CSV
with open('backend/data/mock_billing_data_updated.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print("Addresses replaced successfully!")