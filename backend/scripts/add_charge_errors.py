import pandas as pd
import numpy as np
import random

def add_charge_errors():
    # Load the mock billing data
    print("Loading mock billing data...")
    df = pd.read_csv('../data/mock_billing_data.csv')
    
    # Get total number of rows
    total_rows = len(df)
    
    # Randomly select 20 rows for charge errors
    print("\nIntroducing charge calculation errors in 20 random bills...")
    error_indices = random.sample(range(total_rows), 20)
    
    for idx in error_indices:
        # Decide if it's a slight error or massive error (70% slight, 30% massive)
        error_type = np.random.choice(['slight', 'massive'], p=[0.7, 0.3])
        
        original_charge = df.loc[idx, 'latest_charges']
        
        if error_type == 'slight':
            # Slight error: +/- 5-15%
            factor = np.random.uniform(0.85, 0.95) if np.random.random() < 0.5 else np.random.uniform(1.05, 1.15)
        else:
            # Massive error: +/- 50-200%
            factor = np.random.uniform(0.3, 0.5) if np.random.random() < 0.5 else np.random.uniform(1.5, 3.0)
        
        # Apply the factor to the original charge
        new_charge = original_charge * factor
        
        # Round to 2 decimal places
        new_charge = round(new_charge, 2)
        
        # Update the charge in the dataframe
        df.loc[idx, 'latest_charges'] = new_charge
        
        print(f"Row {idx}: Changed charge from {original_charge:.2f} to {new_charge:.2f} ({error_type} error)")
    
    # Save the data with charge errors
    print("\nSaving data with charge errors...")
    df.to_csv('../data/mock_billing_data_with_errors.csv', index=False)
    print("Done! Data with charge errors saved to 'mock_billing_data_with_errors.csv'")

if __name__ == "__main__":
    add_charge_errors()