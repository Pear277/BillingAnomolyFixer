import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tool_wrapper import billing_clean_fixer_tool

result = billing_clean_fixer_tool.run({
    "billing_path": "backend/data/mock_billing_data.csv",
    "reference_folder": "backend/data/opname_csv_gb/Data",
    "output_path": "backend/data/cleaned_billing_streetfix.csv"
})

print(result)
