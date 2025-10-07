"""Plotly-based chart creation."""
from __future__ import annotations

import pathlib
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from riskarb.analysis.spread import DealMetrics


def save_price_probability_chart(
    metrics: DealMetrics, target_history: pd.DataFrame, output_dir: pathlib.Path
) -> Optional[pathlib.Path]:
    if target_history.empty:
        return None

    figure = make_subplots(specs=[[{"secondary_y": True}]])

    figure.add_trace(
        go.Scatter(
            x=target_history.index,
            y=target_history["Close"],
            name=f"{metrics.deal.target_ticker} Close",
        ),
        secondary_y=False,
    )

    if metrics.implied_probability is not None:
        figure.add_trace(
            go.Scatter(
                x=[target_history.index[-1]],
                y=[metrics.implied_probability * 100],
                mode="markers",
                marker=dict(color="green", size=10),
                name="Implied Probability (%)",
            ),
            secondary_y=True,
        )

    figure.update_layout(
        title=(
            f"{metrics.deal.target_name} ({metrics.deal.target_ticker})"
            f" – Deal Spread"
        ),
        xaxis_title="Date",
        yaxis_title="Target Price (USD)",
    )
    figure.update_yaxes(title_text="Implied Probability (%)", secondary_y=True, range=[0, 100])

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{metrics.deal.target_ticker}_chart.html"
    figure.write_html(str(output_path))
    return output_path
