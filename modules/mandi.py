"""Mandi (market) price data loader."""

import json
import logging
from pathlib import Path

from modules.weather import DISTRICTS

logger = logging.getLogger(__name__)

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "mandi_prices.json"


def get_mandi_prices(district_name: str) -> dict:
    """Return crop price dict for the region of the given district."""
    try:
        district = DISTRICTS.get(district_name)
        if not district:
            return {}

        region = district["region"]

        with open(_DATA_PATH, encoding="utf-8") as f:
            all_prices = json.load(f)

        return all_prices.get(region, {})
    except Exception as exc:
        logger.error("Mandi price load failed: %s", exc)
        return {}
