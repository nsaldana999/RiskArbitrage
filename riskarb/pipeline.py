"""High level pipeline that orchestrates data collection and reporting."""
from __future__ import annotations

import datetime as dt
import json
import pathlib
from typing import Iterable, List, Tuple

import pandas as pd

from riskarb.analysis.market import PriceHistory, fetch_history
from riskarb.analysis.spread import DealMetrics, compute_metrics
from riskarb.config import APISettings
from riskarb.data_sources.fmp import Deal, fetch_deals, summarise
from riskarb.visualization.charts import save_price_probability_chart


def _deal_to_metrics(deal: Deal) -> Tuple[DealMetrics, PriceHistory, PriceHistory | None]:
    start = deal.announcement_date - dt.timedelta(days=120)
    target_history = fetch_history(deal.target_ticker, start=start)
    acquirer_history = None
    if deal.acquirer_ticker:
        acquirer_history = fetch_history(deal.acquirer_ticker, start=start)
    metrics = compute_metrics(deal, target_history, acquirer_history)

    return metrics, target_history, acquirer_history


def build_dashboard(
    settings: APISettings,
    output_dir: pathlib.Path,
    lookback_days: int = 180,
) -> List[DealMetrics]:
    since = dt.date.today() - dt.timedelta(days=lookback_days)
    deals = fetch_deals(settings, since=since)

    metrics: List[DealMetrics] = []
    charts_dir = output_dir / "charts"

    for deal in deals:
        metric, target_history, _ = _deal_to_metrics(deal)
        metrics.append(metric)

        save_price_probability_chart(metric, target_history.history, charts_dir)

    summary_path = output_dir / "deals_summary.json"
    summary_path.write_text(json.dumps(summarise(deals), indent=2))

    metrics_df = pd.DataFrame(metric.as_dict() for metric in metrics)
    metrics_path = output_dir / "deal_metrics.csv"
    metrics_df.to_csv(metrics_path, index=False)

    return metrics


def format_table(metrics: Iterable[DealMetrics]) -> pd.DataFrame:
    records = []
    for metric in metrics:
        records.append(
            {
                "Target": metric.deal.target_ticker,
                "Announcement": metric.deal.announcement_date,
                "Status": metric.deal.status,
                "Offer Price": metric.deal.offer_price,
                "Current Price": metric.current_price,
                "Spread %": metric.spread * 100 if metric.spread is not None else None,
                "Implied Probability %":
                    metric.implied_probability * 100 if metric.implied_probability else None,
            }
        )
    return pd.DataFrame.from_records(records)
