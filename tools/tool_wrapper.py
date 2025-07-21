from langchain.tools import Tool
from backend.data.ingest_and_address_fix import BillingDataFixer


# Create an instance of your fixer agent
fixer = BillingDataFixer()

# Wrap the 'run' method as a LangChain tool
billing_clean_fixer_tool = Tool.from_function(
    func=fixer.run,
    name="billing_clean_fixer",
    description="Cleans billing data and corrects UK street name typos using fuzzy matching and OS Open Names reference.",
    return_direct=True
)
