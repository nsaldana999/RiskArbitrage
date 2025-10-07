"""Utilities for fetching merger data from Financial Modeling Prep."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Iterable, List, Optional

import requests

from riskarb.config import APISettings

HSR_THRESHOLD_2024 = 119_500_000  # USD, adjusted annually.


@dataclass
class Deal:
    """Represents a merger or acquisition deal."""

    announcement_date: dt.date
    status: str
    deal_type: str
    deal_value: Optional[float]
    offer_price: Optional[float]
    target_ticker: str
    target_name: str
    acquirer_ticker: Optional[str]
    acquirer_name: Optional[str]
    exchange_ratio: Optional[float]
    cash_component: Optional[float]
    source: str = "FinancialModelingPrep"

    @property
    def is_pending(self) -> bool:
        return self.status.lower() in {"pending", "rumor", "announced"}

    @property
    def is_large_enough(self) -> bool:
        return (self.deal_value or 0) >= HSR_THRESHOLD_2024


API_ENDPOINT = "https://financialmodelingprep.com/api/v4/mergers-and-acquisitions"


def _parse_date(raw: str) -> Optional[dt.date]:
    if not raw:
        return None
    try:
        return dt.datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return None


def _normalise_deal(raw: dict) -> Optional[Deal]:
    announcement_date = _parse_date(raw.get("announcementDate"))
    if not announcement_date:
        return None

    deal = Deal(
        announcement_date=announcement_date,
        status=raw.get("dealStatus", "").strip(),
        deal_type=raw.get("dealType", "").strip(),
        deal_value=raw.get("dealValue"),
        offer_price=raw.get("dealPrice"),
        target_ticker=(raw.get("targetTicker") or "").strip().upper(),
        target_name=(raw.get("targetName") or "").strip(),
        acquirer_ticker=(raw.get("acquirerTicker") or "").strip().upper() or None,
        acquirer_name=(raw.get("acquirerName") or "").strip() or None,
        exchange_ratio=raw.get("exchangeRatio"),
        cash_component=raw.get("cashComponent"),
    )
    if not deal.target_ticker:
        return None
    return deal


def fetch_deals(settings: APISettings, since: Optional[dt.date] = None) -> List[Deal]:
    """Fetch merger deals from the API.

    Parameters
    ----------
    settings:
        API settings containing the Financial Modeling Prep key.
    since:
        Only deals announced on or after this date are returned.
    """

    params = {"apikey": settings.financial_modeling_prep_key}
    if since:
        params["from"] = since.isoformat()

    response = requests.get(API_ENDPOINT, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    deals: List[Deal] = []
    for raw_deal in payload:
        deal = _normalise_deal(raw_deal)
        if not deal:
            continue
        if since and deal.announcement_date < since:
            continue
        if not deal.is_pending:
            continue
        if not deal.is_large_enough:
            continue
        deals.append(deal)
    return deals


def summarise(deals: Iterable[Deal]) -> List[dict]:
    """Convert deals into JSON-serialisable dictionaries."""

    summary: List[dict] = []
    for deal in deals:
        summary.append(
            {
                "announcement_date": deal.announcement_date.isoformat(),
                "status": deal.status,
                "deal_type": deal.deal_type,
                "deal_value": deal.deal_value,
                "offer_price": deal.offer_price,
                "target_ticker": deal.target_ticker,
                "target_name": deal.target_name,
                "acquirer_ticker": deal.acquirer_ticker,
                "acquirer_name": deal.acquirer_name,
                "exchange_ratio": deal.exchange_ratio,
                "cash_component": deal.cash_component,
                "source": deal.source,
            }
        )
    return summary
