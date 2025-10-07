"""Spread and probability calculations."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Optional

from riskarb.analysis.market import PriceHistory
from riskarb.data_sources.fmp import Deal


@dataclass
class DealMetrics:
    deal: Deal
    current_price: Optional[float]
    spread: Optional[float]
    implied_probability: Optional[float]
    break_price: Optional[float]

    def as_dict(self) -> dict:
        return {
            "target_ticker": self.deal.target_ticker,
            "announcement_date": self.deal.announcement_date.isoformat(),
            "deal_status": self.deal.status,
            "deal_type": self.deal.deal_type,
            "deal_value": self.deal.deal_value,
            "offer_price": self.deal.offer_price,
            "break_price": self.break_price,
            "current_price": self.current_price,
            "spread": self.spread,
            "implied_probability": self.implied_probability,
        }


def _compute_break_price(history: PriceHistory, announcement_date: dt.date) -> Optional[float]:
    """Use the close from the last trading day before announcement as break price."""

    day = announcement_date - dt.timedelta(days=1)
    for _ in range(7):
        price = history.price_on(day)
        if price is not None:
            return price
        day -= dt.timedelta(days=1)
    return None


def _compute_offer_value(deal: Deal, acquirer_price: Optional[float]) -> Optional[float]:
    if deal.offer_price:
        return deal.offer_price
    if deal.exchange_ratio and acquirer_price:
        total = deal.exchange_ratio * acquirer_price
        if deal.cash_component:
            total += deal.cash_component
        return total
    return None


def compute_metrics(
    deal: Deal,
    target_history: PriceHistory,
    acquirer_history: Optional[PriceHistory] = None,
) -> DealMetrics:
    offer_value = _compute_offer_value(
        deal, acquirer_history.latest_close() if acquirer_history else None
    )

    current_price = target_history.latest_close()
    break_price = _compute_break_price(target_history, deal.announcement_date)

    spread = None
    implied_probability = None

    if offer_value and current_price:
        spread = (offer_value - current_price) / offer_value
        if break_price and offer_value != break_price:
            implied_probability = max(
                0.0,
                min(1.0, (current_price - break_price) / (offer_value - break_price)),
            )

    return DealMetrics(
        deal=deal,
        current_price=current_price,
        spread=spread,
        implied_probability=implied_probability,
        break_price=break_price,
    )
