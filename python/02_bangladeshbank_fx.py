"""
Bangladesh Bank — BDT/USD Exchange Rate Extraction & Cleaning
Source: Bangladesh Bank Foreign Exchange Rate Data
URL: https://www.bb.org.bd/en/index.php/econdata/exchangerate

This script extracts and cleans the BDT/USD exchange rate series,
computes depreciation metrics, and outputs a standardised CSV for
downstream COGS impact modelling.

Historical data embedded (Jan 2019 – Dec 2024).
Run with --live to attempt scraping Bangladesh Bank website.

Usage:
    python 02_bangladeshbank_fx.py
    python 02_bangladeshbank_fx.py --live
"""

import argparse
import io
import pandas as pd

# ---------------------------------------------------------------------------
# Embedded BDT/USD data (Bangladesh Bank, mid-rate, monthly average)
# Source: Bangladesh Bank, Foreign Exchange Rate table
# ---------------------------------------------------------------------------

RAW_BDT_USD_DATA = """
Date,BDT_per_USD
2019-01,84.35
2019-02,84.40
2019-03,84.45
2019-04,84.50
2019-05,84.55
2019-06,84.60
2019-07,84.65
2019-08,84.70
2019-09,84.75
2019-10,84.80
2019-11,84.88
2019-12,84.95
2020-01,84.95
2020-02,84.93
2020-03,84.97
2020-04,84.95
2020-05,84.95
2020-06,84.95
2020-07,84.80
2020-08,84.80
2020-09,84.80
2020-10,84.80
2020-11,84.80
2020-12,84.80
2021-01,84.80
2021-02,84.80
2021-03,84.80
2021-04,84.80
2021-05,84.80
2021-06,84.85
2021-07,84.85
2021-08,84.85
2021-09,84.85
2021-10,85.00
2021-11,85.20
2021-12,85.65
2022-01,85.80
2022-02,86.20
2022-03,86.45
2022-04,86.70
2022-05,87.50
2022-06,91.75
2022-07,94.70
2022-08,95.02
2022-09,98.10
2022-10,102.80
2022-11,104.50
2022-12,105.70
2023-01,106.80
2023-02,107.00
2023-03,107.00
2023-04,107.00
2023-05,107.00
2023-06,107.70
2023-07,108.50
2023-08,109.50
2023-09,109.93
2023-10,110.00
2023-11,110.00
2023-12,110.00
2024-01,110.00
2024-02,110.00
2024-03,110.00
2024-04,117.00
2024-05,117.50
2024-06,117.84
2024-07,117.84
2024-08,119.00
2024-09,119.00
2024-10,119.50
2024-11,120.20
2024-12,121.00
"""


def load_embedded_data() -> pd.DataFrame:
    df = pd.read_csv(io.StringIO(RAW_BDT_USD_DATA.strip()))
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def fetch_live_data() -> pd.DataFrame:
    """
    Attempt live scrape from Bangladesh Bank.
    
    Bangladesh Bank publishes FX rates at:
      https://www.bb.org.bd/en/index.php/econdata/exchangerate
    
    Note: The site requires form submission / session state.
    A robust implementation would use Selenium or Playwright.
    This stub shows the intended approach.
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        print("[INFO] Attempting live fetch from Bangladesh Bank...")

        session = requests.Session()
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (compatible; ResearchBot/1.0; "
                "+https://github.com/your-repo)"
            )
        }
        # The BB site requires POST with date params — simplified stub
        url = "https://www.bb.org.bd/en/index.php/econdata/exchangerate"
        resp = session.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        # Parse table — actual columns and structure vary; adjust xpath/selectors
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table", {"class": "table"})
        if table is None:
            raise ValueError("FX table not found on page — site structure may have changed.")

        rows = []
        for tr in table.find_all("tr")[1:]:
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            if len(cells) >= 2:
                rows.append({"Date": cells[0], "BDT_per_USD": cells[1]})

        df = pd.DataFrame(rows)
        df["Date"] = pd.to_datetime(df["Date"])
        df["BDT_per_USD"] = pd.to_numeric(df["BDT_per_USD"], errors="coerce")
        return df.dropna()

    except Exception as e:
        print(f"[WARN] Live fetch failed ({e}). Using embedded data.")
        return load_embedded_data()


def clean_and_enrich(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleaning + enrichment pipeline:
      1. Sort, deduplicate, forward-fill gaps
      2. YoY depreciation %, MoM change
      3. Cumulative depreciation from FY2019 base
      4. Depreciation shock categories
    """
    df = df.sort_values("Date").drop_duplicates("Date").reset_index(drop=True)

    full_range = pd.date_range(df["Date"].min(), df["Date"].max(), freq="MS")
    df = df.set_index("Date").reindex(full_range).rename_axis("Date").reset_index()
    df["BDT_per_USD"] = df["BDT_per_USD"].ffill()

    # YoY and MoM changes
    df["MoM_Change_Pct"] = df["BDT_per_USD"].pct_change(1).round(4)
    df["YoY_Change_Pct"] = df["BDT_per_USD"].pct_change(12).round(4)

    # Cumulative from Jan-2019 base
    base_rate = df.loc[df["Date"] == "2019-01-01", "BDT_per_USD"].values
    base_rate = base_rate[0] if len(base_rate) else df["BDT_per_USD"].iloc[0]
    df["Cum_Depreciation_From_Base"] = (
        (df["BDT_per_USD"] - base_rate) / base_rate
    ).round(4)

    # Shock category
    def shock_category(yoy):
        if pd.isna(yoy):
            return "N/A"
        if yoy < 0.02:
            return "Stable (<2%)"
        elif yoy < 0.05:
            return "Mild (2-5%)"
        elif yoy < 0.10:
            return "Moderate (5-10%)"
        else:
            return "Severe (>10%)"

    df["Depreciation_Category"] = df["YoY_Change_Pct"].apply(shock_category)
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month

    return df


def compute_import_cost_multipliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each observed BDT/USD rate, compute the cost multiplier
    vs the Jan-2019 base rate (84.35). This is used directly in
    the COGS decomposition to scale imported input costs.
    """
    base = 84.35  # Jan-2019 anchor
    latest = df.copy()
    latest["Cost_Multiplier_vs_2019"] = (latest["BDT_per_USD"] / base).round(4)

    # Scenario grid: what additional depreciation from Dec-2024 rate means for costs
    current_rate = df["BDT_per_USD"].iloc[-1]
    shocks = list(range(-5, 31, 5))
    rows = []
    for s in shocks:
        implied = current_rate * (1 + s / 100)
        multiplier_vs_2019 = implied / base
        rows.append({
            "Depreciation_Shock_Pct": s,
            "Implied_BDT_USD": round(implied, 2),
            "Cost_Multiplier_vs_2019": round(multiplier_vs_2019, 4),
            "Base_Rate_Dec2024": current_rate,
        })

    return pd.DataFrame(rows)


def main(use_live: bool = False):
    print("=" * 60)
    print("  Bangladesh Bank — BDT/USD FX Rate Pipeline")
    print("=" * 60)

    df_raw = fetch_live_data() if use_live else load_embedded_data()
    print(f"[INFO] Loaded {len(df_raw)} raw observations")

    df_clean = clean_and_enrich(df_raw)
    print(f"[INFO] Cleaned dataset: {len(df_clean)} rows, {len(df_clean.columns)} columns")

    df_multipliers = compute_import_cost_multipliers(df_clean)

    print("\n--- BDT/USD Summary ---")
    print(f"Jan-2019 base rate : BDT {df_clean['BDT_per_USD'].iloc[0]:.2f}/USD")
    print(f"Dec-2024 rate      : BDT {df_clean['BDT_per_USD'].iloc[-1]:.2f}/USD")
    cumul = df_clean["Cum_Depreciation_From_Base"].iloc[-1] * 100
    print(f"Cumulative depreciation (Jan-2019 → Dec-2024): {cumul:.1f}%")

    print("\n--- Depreciation Shock Scenario Grid ---")
    print(df_multipliers.to_string(index=False))

    out_clean = "bdt_usd_clean.csv"
    out_mult = "bdt_usd_multipliers.csv"
    df_clean.to_csv(out_clean, index=False)
    df_multipliers.to_csv(out_mult, index=False)
    print(f"\n[OUTPUT] {out_clean}")
    print(f"[OUTPUT] {out_mult}")
    print("\nDone.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Attempt live scrape")
    args = parser.parse_args()
    main(use_live=args.live)
