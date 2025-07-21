from backend.data.ingest_and_address_fix import BillingDataFixer

fixer = BillingDataFixer()
result = fixer.run(
    billing_path="backend/data/cleaned_billing_data2.csv",
    reference_folder="backend/data/opname_csv_gb",
    output_path="backend/data/cleaned_billing_streetfix.csv"
)

print(result)
