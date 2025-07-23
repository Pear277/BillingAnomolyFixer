from langchain.tools import BaseTool
from backend.utils.ingest_and_address_fix import BillingDataFixer
from pydantic import BaseModel

# Define argument schema for validation
class BillingFixerArgs(BaseModel):
    billing_path: str
    reference_folder: str
    output_path: str

class BillingCleanFixerTool(BaseTool):
    name = "billing_clean_fixer"
    description = "Cleans billing data and corrects UK street name typos using fuzzy matching and OS Open Names reference."
    args_schema = BillingFixerArgs

    def _run(self, billing_path: str, reference_folder: str, output_path: str) -> str:
        fixer = BillingDataFixer()
        return fixer.run(billing_path, reference_folder, output_path)

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported.")
