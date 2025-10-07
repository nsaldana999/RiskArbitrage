#!/usr/bin/env python
"""Entry point to refresh the risk arbitrage dashboard."""
from __future__ import annotations

import argparse
import pathlib

from riskarb.config import APISettings, MissingAPIKeyError
from riskarb.pipeline import build_dashboard, format_table


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("reports"),
        help="Directory where generated artifacts are stored.",
    )
    parser.add_argument(
        "--lookback",
        type=int,
        default=180,
        help="Number of days to look back for deals.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        settings = APISettings.from_env()
    except MissingAPIKeyError as exc:
        raise SystemExit(str(exc))

    metrics = build_dashboard(settings, args.output, lookback_days=args.lookback)

    table = format_table(metrics)
    table_path = args.output / "dashboard_table.csv"
    table.to_csv(table_path, index=False)
    print(f"Updated {len(metrics)} deals. Summary table saved to {table_path}.")


if __name__ == "__main__":
    main()
