from utils.ingest_and_address_fix import BillingDataFixer
from crewai.tools import tool
import os

@tool("auto_fix_tool")
def auto_fix_tool(billing_path: str, reference_folder: str, output_path: str) -> str:
    """
    Cleans billing data by fixing date formatting issues and correcting typos in UK addresses.
    
    Args:
        billing_path (str): Path to the input billing CSV file.
        reference_folder (str): Path to the folder containing reference data for address correction.
        output_path (str): Path where the cleaned billing data will be saved.
        
    Returns:
        str: A message indicating the result of the cleaning operation.
    """
    
    # Try different path variations for billing_path
    if not os.path.exists(billing_path):
        alt_path = billing_path.replace('backend/', '')
        if os.path.exists(alt_path):
            billing_path = alt_path
    
    # Try different path variations for reference_folder
    if not os.path.exists(reference_folder):
        alt_ref = reference_folder.replace('backend/', '')
        if os.path.exists(alt_ref):
            reference_folder = alt_ref
    
    # Try different path variations for output_path
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        alt_output_dir = output_dir.replace('backend/', '')
        if os.path.exists(alt_output_dir):
            output_path = output_path.replace('backend/', '')
        else:
            # Create the directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

    fixer = BillingDataFixer()
    result = fixer.run(billing_path, reference_folder, output_path)
    return result