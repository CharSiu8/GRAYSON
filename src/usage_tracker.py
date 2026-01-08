# ================================================================================
# WHAT THIS FILE IS:
# Usage tracker for monitoring and limiting OpenAI API costs.
#
# WHY YOU NEED IT:
# - Tracks token usage and calculates costs
# - Enforces monthly spending limit ($10/month)
# - Auto-resets on the 1st of each month
# - Prevents runaway API costs
# ================================================================================

"""Usage tracking and cost limiting for OpenAI API calls."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Tuple

# Pricing per token (as of 2024)
PRICING = {
    "text-embedding-3-small": 0.02 / 1_000_000,  # $0.02 per 1M tokens
    "gpt-3.5-turbo-input": 0.50 / 1_000_000,     # $0.50 per 1M tokens
    "gpt-3.5-turbo-output": 1.50 / 1_000_000,    # $1.50 per 1M tokens
}

MONTHLY_LIMIT = 5.00  # $5 per month

# Store usage data in the project root
USAGE_FILE = Path(__file__).parent.parent / "usage_data.json"


def _get_current_month() -> str:
    """Get current month as YYYY-MM string."""
    return datetime.now().strftime("%Y-%m")


def _load_usage() -> dict:
    """Load usage data from file."""
    if USAGE_FILE.exists():
        try:
            with open(USAGE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"month": _get_current_month(), "total_cost": 0.0, "breakdown": {}}


def _save_usage(data: dict) -> None:
    """Save usage data to file."""
    with open(USAGE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _maybe_reset_month(data: dict) -> dict:
    """Reset usage if we're in a new month."""
    current_month = _get_current_month()
    if data.get("month") != current_month:
        return {"month": current_month, "total_cost": 0.0, "breakdown": {}}
    return data


def check_usage_limit() -> Tuple[bool, float, str]:
    """Check if usage limit has been reached.

    Returns:
        Tuple of (is_allowed, remaining_budget, message)
    """
    data = _load_usage()
    data = _maybe_reset_month(data)
    _save_usage(data)

    total_cost = data.get("total_cost", 0.0)
    remaining = MONTHLY_LIMIT - total_cost

    if total_cost >= MONTHLY_LIMIT:
        next_month = datetime.now().replace(day=1, month=datetime.now().month % 12 + 1)
        if datetime.now().month == 12:
            next_month = next_month.replace(year=datetime.now().year + 1)
        return (
            False,
            0.0,
            f"Monthly usage limit (${MONTHLY_LIMIT:.2f}) reached. "
            f"Service will resume on {next_month.strftime('%B 1, %Y')}."
        )

    return (True, remaining, "")


def record_usage(model_type: str, tokens: int) -> float:
    """Record token usage and return the cost.

    Args:
        model_type: One of 'text-embedding-3-small', 'gpt-3.5-turbo-input', 'gpt-3.5-turbo-output'
        tokens: Number of tokens used

    Returns:
        Cost in dollars for this usage
    """
    data = _load_usage()
    data = _maybe_reset_month(data)

    price_per_token = PRICING.get(model_type, 0)
    cost = tokens * price_per_token

    data["total_cost"] = data.get("total_cost", 0.0) + cost

    # Track breakdown by model type
    if "breakdown" not in data:
        data["breakdown"] = {}
    data["breakdown"][model_type] = data["breakdown"].get(model_type, 0.0) + cost

    _save_usage(data)
    return cost


def get_usage_stats() -> dict:
    """Get current usage statistics."""
    data = _load_usage()
    data = _maybe_reset_month(data)
    _save_usage(data)

    return {
        "month": data.get("month"),
        "total_cost": data.get("total_cost", 0.0),
        "limit": MONTHLY_LIMIT,
        "remaining": max(0, MONTHLY_LIMIT - data.get("total_cost", 0.0)),
        "breakdown": data.get("breakdown", {}),
    }
