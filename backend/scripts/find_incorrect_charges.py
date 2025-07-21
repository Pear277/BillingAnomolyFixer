import pandas as pd

def find_incorrect_charges():
    # Load the mock billing data
    df = pd.read_csv('../data/mock_billing_data.csv')
    
    # Calculate the correct charges
    df['correct_charges'] = (
        df['fresh_water_usage'] * df['fresh_water_rate'] +
        df['waste_water_usage'] * df['waste_water_rate'] +
        df['fresh_water_fixed_charge'] +
        df['waste_water_fixed_charge']
    ).round(2)
    
    # Find rows with charge discrepancies (allowing for small rounding differences)
    discrepancies = df[abs(df['latest_charges'] - df['correct_charges']) > 0.5]
    
    # Extract and print the account numbers and bill dates with incorrect charges
    print("Account numbers and bill dates with incorrect charges:")
    print("=====================================================")
    print("ACCOUNT_NUMBER, BILL_DATE, ACTUAL_CHARGE, CORRECT_CHARGE, DIFFERENCE")
    
    for _, row in discrepancies.iterrows():
        diff = row['latest_charges'] - row['correct_charges']
        print(f"{row['account_number']}, {row['bill_date']}, {row['latest_charges']:.2f}, {row['correct_charges']:.2f}, {diff:.2f}")
    
    print(f"\nTotal incorrect charges found: {len(discrepancies)}")
    
    # Save the results to a CSV file
    result_df = discrepancies[['account_number', 'bill_date', 'latest_charges', 'correct_charges']]
    result_df['difference'] = result_df['latest_charges'] - result_df['correct_charges']
    result_df.to_csv('../data/incorrect_charges.csv', index=False)
    print("Results saved to 'incorrect_charges.csv'")

if __name__ == "__main__":
    find_incorrect_charges()