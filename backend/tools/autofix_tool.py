from utils.ingest_and_address_fix import BillingDataFixer
from crewai.tools import tool

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

    fixer = BillingDataFixer()
    result = fixer.run(billing_path, reference_folder, output_path)
    return result