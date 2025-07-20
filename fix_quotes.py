import csv

# Read the CSV file
with open('backend/data/mock_billing_data_updated.csv', 'r') as f:
    content = f.read()

# Replace triple quotes with single quotes
fixed_content = content.replace('"""', '"')

# Write the fixed content back
with open('backend/data/mock_billing_data_updated.csv', 'w', newline='') as f:
    f.write(fixed_content)

print("Fixed quotes in CSV file")