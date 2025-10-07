# Risk Arbitrage Tracker

This repository provides an automated workflow for monitoring spreads on US merger and acquisition deals that are large enough to fall under the Hart-Scott-Rodino (HSR) review threshold.

The project ingests live merger data, pulls market prices for both acquirers and targets, and calculates the implied probability that each transaction will close based on the market-implied spread. Interactive Plotly charts overlay the target's price history with the latest probability estimate and are exported to the `reports/` directory.

## Features

- **Automated deal sourcing** – Uses the [Financial Modeling Prep](https://financialmodelingprep.com/developer/docs/mergers-and-acquisitions-api) mergers API to fetch the latest pending transactions. Deals are filtered to those with an announced value above the 2024 HSR size-of-transaction threshold ($119.5mm).
- **Real-time market data** – Downloads price history for each target (and acquirer for stock or mixed considerations) with [`yfinance`](https://github.com/ranaroussi/yfinance).
- **Spread analytics** – Computes spreads and market-implied probabilities using the latest close, the offer price, and a break price derived from the pre-announcement trading level.
- **Visualization** – Generates interactive HTML charts that overlay the target price history with the current probability estimate.
- **GitHub Automation ready** – Ships with a CLI that can be wired into a scheduled GitHub Actions workflow to refresh the dataset without manual intervention.

## Quick start

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Provide API credentials**

   Export your Financial Modeling Prep API key before running the pipeline:

   ```bash
   export FMP_API_KEY="your-api-key"
   ```

3. **Generate the dashboard artifacts**

   ```bash
   python scripts/update_dashboard.py --output reports --lookback 180
   ```

   This command writes three types of artifacts to the specified output directory:

   - `deals_summary.json`: raw deal metadata returned by the API.
   - `deal_metrics.csv`: calculated spreads, break prices, and implied probabilities.
   - `dashboard_table.csv`: a concise table suitable for publishing or further analysis.
   - `charts/*.html`: per-deal interactive charts that overlay price history and probability.

## Automating updates with GitHub Actions

Add a scheduled workflow (e.g. `.github/workflows/update-dashboard.yml`) containing the following steps:

```yaml
name: Update risk arbitrage dashboard

on:
  schedule:
    - cron: "0 22 * * 1-5"  # Run after market close on weekdays
  workflow_dispatch:

jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Refresh dashboard
        env:
          FMP_API_KEY: ${{ secrets.FMP_API_KEY }}
        run: python scripts/update_dashboard.py --output reports --lookback 180
      - name: Commit results
        run: |
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git add reports
          git commit -m "Automated dashboard refresh" || echo "No changes"
          git push
```

## Roadmap

- Enhance deal sourcing with additional feeds (FTC early termination list, SEC 425 filings) to avoid reliance on a single provider.
- Integrate alternative break-price models (e.g. regression-based or volatility-adjusted estimates).
- Publish a lightweight front-end that consumes the generated CSV/JSON and renders a consolidated dashboard page.
