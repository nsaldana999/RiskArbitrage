"""Market data utilities."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Optional

import pandas as pd
import yfinance as yf


@dataclass
class PriceHistory:
    ticker: str
    history: pd.DataFrame

    def latest_close(self) -> Optional[float]:
        if self.history.empty:
            return None
        return float(self.history["Close"].iloc[-1])

    def price_on(self, date: dt.date) -> Optional[float]:
        if self.history.empty:
            return None
        try:
            return float(self.history.loc[str(date)]["Close"])
        except KeyError:
            return None


def fetch_history(ticker: str, start: dt.date, end: Optional[dt.date] = None) -> PriceHistory:
    """Download daily price history for a ticker."""

    if end is None:
        end = dt.date.today() + dt.timedelta(days=1)
    data = yf.download(ticker, start=start, end=end, interval="1d", progress=False)
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame()
    return PriceHistory(ticker=ticker, history=data)
