"""
Tool: search AWS invoices/billing line items for anomalies over a date range.
In production this would query Cost & Usage Reports (CUR) stored in S3/Athena
or the AWS Cost Explorer API. Here it reads a seeded sample dataset so the
agent's reasoning path can be demoed end-to-end without live AWS credentials.
"""
import json
import os

from langchain_core.tools import tool

SAMPLE_INVOICE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "seed_data", "sample_invoice.json"
)


@tool
def search_invoices(month: str) -> str:
    """Look up AWS invoice line items for a given month (format: 'YYYY-MM').
    Returns per-service cost breakdown so anomalies can be spotted."""
    with open(SAMPLE_INVOICE_PATH) as f:
        data = json.load(f)

    month_data = data.get(month)
    if not month_data:
        available = ", ".join(data.keys())
        return f"No invoice data for {month}. Available months: {available}"

    lines = [f"AWS invoice summary for {month} (total: ${month_data['total']:.2f}):"]
    for service, cost in month_data["by_service"].items():
        lines.append(f"  - {service}: ${cost:.2f}")
    return "\n".join(lines)
