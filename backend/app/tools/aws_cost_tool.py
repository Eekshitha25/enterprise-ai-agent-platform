"""
Tool: query live (or mocked) AWS Cost Explorer usage data to correlate
billing spikes with actual resource usage changes.
"""
import json
import os
from datetime import datetime

import boto3
from langchain_core.tools import tool

from app.core.config import get_settings

settings = get_settings()

SAMPLE_USAGE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "seed_data", "sample_usage.json"
)


def _mock_usage(month: str) -> str:
    if not os.path.exists(SAMPLE_USAGE_PATH):
        return "No mock usage data seeded."
    with open(SAMPLE_USAGE_PATH) as f:
        data = json.load(f)
    month_data = data.get(month)
    if not month_data:
        return f"No usage data for {month}."
    lines = [f"AWS resource usage deltas for {month} vs prior month:"]
    for item in month_data:
        lines.append(
            f"  - {item['service']}: {item['metric']} changed {item['delta_pct']:+.1f}% "
            f"({item['note']})"
        )
    return "\n".join(lines)


def _live_usage(month: str) -> str:
    """Real Cost Explorer call — requires AWS creds with ce:GetCostAndUsage."""
    client = boto3.client(
        "ce",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )
    start = datetime.strptime(month, "%Y-%m").strftime("%Y-%m-01")
    year, mon = month.split("-")
    end_month = int(mon) % 12 + 1
    end_year = int(year) + (1 if end_month == 1 else 0)
    end = f"{end_year}-{end_month:02d}-01"

    response = client.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost", "UsageQuantity"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )
    lines = [f"AWS usage for {month}:"]
    for group in response["ResultsByTime"][0]["Groups"]:
        service = group["Keys"][0]
        cost = group["Metrics"]["UnblendedCost"]["Amount"]
        lines.append(f"  - {service}: ${float(cost):.2f}")
    return "\n".join(lines)


@tool
def get_cloud_usage(month: str) -> str:
    """Check AWS resource usage (compute hours, storage, data transfer) for a
    given month (format 'YYYY-MM') to correlate against billing changes."""
    if settings.use_mock_aws_tool:
        return _mock_usage(month)
    return _live_usage(month)
