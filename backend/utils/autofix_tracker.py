import pandas as pd
import json
import re
from datetime import datetime

class AutofixTracker:
    def __init__(self):
        self.changes = []
        self.address_corrections = set()  # Track unique address corrections
    
    def track_date_fix(self, account_number, bill_date, field, original, fixed):
        """Track date formatting fixes - only for year-first formats like 2019/02/01"""
        # Only track if original format starts with year (4 digits followed by / or -)
        if re.match(r'^\d{4}[/-]', str(original)):
            self.changes.append({
                "account_number": account_number,
                "bill_date": bill_date,
                "change_type": "date_format_year_first",
                "field": field,
                "original_value": original,
                "fixed_value": fixed,
                "timestamp": datetime.now().isoformat()
            })
    
    def track_address_fix(self, account_number, bill_date, original_address, fixed_address):
        """Track address corrections - only unique spelling corrections"""
        # Extract street names for comparison
        orig_street = original_address.split(',')[0].strip()
        fixed_street = fixed_address.split(',')[0].strip()
        
        # Only track if streets are different (spelling correction)
        if orig_street != fixed_street:
            correction_key = (orig_street, fixed_street)
            
            # Only log each unique correction once
            if correction_key not in self.address_corrections:
                self.address_corrections.add(correction_key)
                self.changes.append({
                    "account_number": account_number,
                    "bill_date": bill_date,
                    "change_type": "address_spelling_correction",
                    "field": "address",
                    "original_value": orig_street,
                    "fixed_value": fixed_street,
                    "timestamp": datetime.now().isoformat()
                })
    
    def track_numeric_fix(self, account_number, bill_date, field, original, fixed):
        """Track numeric value fixes - disabled for minimal tracking"""
        pass
    
    def save_changes(self, output_path):
        """Save all tracked changes to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(self.changes, f, indent=2)
        return len(self.changes)
    
    def get_summary(self):
        """Get summary of changes by type"""
        summary = {}
        for change in self.changes:
            change_type = change['change_type']
            summary[change_type] = summary.get(change_type, 0) + 1
        return summary