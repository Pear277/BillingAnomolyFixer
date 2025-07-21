import pandas as pd
import math

def validate_and_suggest(row):
    issues = []
    suggestions = {}

    # Check usage mismatch
    if row["fresh_water_usage"] != row["waste_water_usage"]:
        issues.append("Fresh/Waste water usage mismatch")

    # Calculate expected charge using given usage values
    expected_charge = round(
        row["fresh_water_usage"] * row["fresh_water_rate"] +
        row["waste_water_usage"] * row["waste_water_rate"] +
        row["fresh_water_fixed_charge"] +
        row["waste_water_fixed_charge"]
    ,2)

    if expected_charge != row["latest_charges"]:
        issues.append("Charge mismatch")
        suggestions["expected_charges"] = round(expected_charge, 2)

        # If usage mismatch also exists, note price likely wrong due to that
        if "Fresh/Waste water usage mismatch" in issues:
            suggestions["note"] = "Price likely incorrect due to usage mismatch"

    return pd.Series({
        "issues": issues,
        "suggestions": suggestions,
        "has_issues": len(issues) > 0
    })

def main():
    # Load your CSV file here
    df = pd.read_csv("backend/data/cleaned_billing_data.csv")

    # Run validation
    results = df.apply(validate_and_suggest, axis=1)

    # Filter flagged bills only
    flagged = results[results['has_issues']]

    # Include identifiers and issues/suggestions columns only
    output = df.loc[flagged.index, ["account_number", "bill_date"]].copy()
    output = pd.concat([output, flagged[["issues", "suggestions"]]], axis=1)

    # Save flagged issues to CSV
    output.to_csv("backend/data/flagged_bills.csv", index=False)

if __name__ == "__main__":
    main()
