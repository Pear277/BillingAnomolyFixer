import csv
import random

# Read the CSV file
with open('backend/data/mock_billing_data_updated.csv', 'r') as f:
    reader = csv.reader(f)
    rows = list(reader)

# Select 3 random customers from each batch of 12
customer_batches = {}
for row in rows[1:]:  # Skip header
    customer_id = row[1]
    batch = int(customer_id.replace('CUST', '')) // 12
    if batch not in customer_batches:
        customer_batches[batch] = set()
    customer_batches[batch].add(customer_id)

selected_customers = []
for batch, customers in customer_batches.items():
    selected = random.sample(list(customers), min(3, len(customers)))
    selected_customers.extend(selected)

# Common typos to introduce
typo_functions = [
    lambda s: s.replace('Street', 'Sreet'),
    lambda s: s.replace('Road', 'Raod'),
    lambda s: s.replace('Square', 'Sqaure'),
    lambda s: s.replace('High', 'Hihg'),
    lambda s: s.replace('Market', 'Marekt'),
    lambda s: s.replace('Bridge', 'Brdige'),
    lambda s: s.replace('Church', 'Chruch'),
    lambda s: s.replace('Broad', 'Braod'),
    lambda s: s.replace('Castle', 'Castel'),
]

# Track which customers have had typos added
customer_typo_count = {cust: 0 for cust in selected_customers}

# Add typos to 1-2 bills per selected customer
for i, row in enumerate(rows[1:], 1):  # Skip header
    customer_id = row[1]
    if customer_id in selected_customers and customer_typo_count[customer_id] < 2:
        # 50% chance to add a typo to this bill
        if random.random() < 0.5:
            address = row[0].strip('"')
            typo_func = random.choice(typo_functions)
            new_address = typo_func(address)
            
            # Only apply if it actually changed something
            if new_address != address:
                rows[i][0] = f'"{new_address}"'
                customer_typo_count[customer_id] += 1

# Write the updated CSV
with open('backend/data/mock_billing_data_updated.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print("Typos added successfully!")