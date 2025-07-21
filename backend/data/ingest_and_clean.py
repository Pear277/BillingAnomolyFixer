import pandas as pd

# Load the CSV file
def load_billing_data(filepath):
    df = pd.read_csv(filepath)
    return df

# Standardize date formats to YYYY-MM-DD

def robust_parse_date(val):
    import pandas as pd
    # Try parsing with dayfirst True
    dt = pd.to_datetime(val, errors='coerce', dayfirst=True)
    if pd.isnull(dt):
        # Try parsing with dayfirst False
        dt = pd.to_datetime(val, errors='coerce', dayfirst=False)
    if pd.isnull(dt):
        return ''  # or return val to keep original if unparseable
    return dt.strftime('%d-%m-%Y')

def standardize_dates(df, date_columns):
    for col in date_columns:
        df[col] = df[col].apply(robust_parse_date)
    return df

# Ensure numeric consistency: usage as int, others as float (2 decimal places)
def numeric_consistency(df):
    # Convert other numeric columns to float with 2 decimals
    float_cols = ['fresh_water_rate', 'fresh_water_fixed_charge', 'waste_water_rate', 'waste_water_fixed_charge', 'latest_charges']
    for col in float_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').round(2)
    return df

# Remove duplicate rows
def remove_duplicates(df):
    return df.drop_duplicates()

# Trim whitespace from string columns
def trim_whitespace(df):
    str_cols = df.select_dtypes(include=['object']).columns
    for col in str_cols:
        df[col] = df[col].str.strip()
    return df

if __name__ == "__main__":
    filepath = "backend/data/mock_billing_data.csv"
    df = load_billing_data(filepath)
    df = standardize_dates(df, ['bill_date', 'billing_period_start', 'billing_period_end'])
    df = numeric_consistency(df)
    df = remove_duplicates(df)
    df = trim_whitespace(df)
    # Save cleaned data for inspection
    df.to_csv("backend/data/cleaned_billing_data.csv", index=False)
    print("Data cleaned and saved to backend/data/cleaned_billing_data.csv")
