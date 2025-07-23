from langchain.tools import BaseTool
from backend.utils.ingest_and_address_fix import BillingDataFixer
from pydantic import BaseModel
from typing import Type


# Define argument schema for validation
class BillingFixerArgs(BaseModel):
    billing_path: str
    reference_folder: str
    output_path: str

class BillingCleanFixerTool(BaseTool):
    name: str = "billing_clean_fixer"
    description: str = "Cleans billing data and corrects UK street name typos using fuzzy matching and OS Open Names reference."
    args_schema: Type[BillingFixerArgs] = BillingFixerArgs


    def _run(self, billing_path: str, reference_folder: str, output_path: str) -> str:
        fixer = BillingDataFixer()
        return fixer.run(billing_path, reference_folder, output_path)

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported.")

# Create the tool instance so it can be imported
billing_clean_fixer_tool = BillingCleanFixerTool()