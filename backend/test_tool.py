# test_tool.py - Create this file and run it
import os
import sys
sys.path.append('.')

from backend.tools.autofix_tool import auto_fix_tool

print("Testing tool directly...")
print("Input file exists:", os.path.exists("backend/data/mock_billing_data.csv"))
print("Reference folder exists:", os.path.exists("backend/data/opname_csv_gb/Data"))

# Create output directory
os.makedirs("backend/data", exist_ok=True)

try:
    result = auto_fix_tool(
        billing_path="data/mock_billing_data.csv",
        reference_folder="backend/data/opname_csv_gb/Data",
        output_path="backend/data/cleaned_billing_streetfix.csv"
    )
    print("Tool result:", result)
    print("Output file created:", os.path.exists("backend/data/cleaned_billing_streetfix.csv"))
except Exception as e:
    print("Tool error:", e)
    import traceback
    traceback.print_exc()