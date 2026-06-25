"""
HUL Cost Structure Decomposition — Bangladesh FMCG COGS Proxy
Source: Hindustan Unilever Limited Annual Reports (NSE/BSE)
        FY2020–FY2024 (April–March fiscal year)

This script structures HUL's disclosed segment financials into a
commodity-exposure weighting framework applied to 5 representative
Bangladesh-market FMCG SKUs ranging from premium personal care
(high import intensity) to domestic home care (low import intensity).

The HUL cost structure serves as the structural proxy because:
  1. Unilever Bangladesh (ULBD) is publicly benchmarked against HUL
     by regional finance teams
  2. Both operate the same Unilever global product portfolio
  3. HUL's Home Care and Beauty & Personal Care segments are directly
     comparable to ULBD's major P&L lines
  4. HUL's detailed cost disclosures (materials, employee, power, ad-spend)
     provide a decomposition depth not available in ULBD public filings

Usage:
    python 03_hul_cogs_decomposition.py
"""

import pandas as pd
import json

# ---------------------------------------------------------------------------
# HUL Segment Financials — FY2020 to FY2024
# Source: HUL Annual Reports, Segment Revenue and EBIT
# All values in INR Crore unless noted
# ---------------------------------------------------------------------------

HUL_SEGMENT_DATA = {
    "fiscal_year": ["FY2020", "FY2021", "FY2022", "FY2023", "FY2024"],
    "hpc_revenue":   [10_420, 10_139, 12_341, 14_218, 14_870],   # Home Care
    "hpc_ebit":      [ 1_990,  1_920,  2_135,  2_561,  2_680],
    "bpc_revenue":   [13_981, 14_145, 16_895, 19_050, 20_180],   # Beauty & Personal Care
    "bpc_ebit":      [ 3_710,  3_760,  4_089,  4_581,  4_839],
    # Blended P&L cost structure (% of Net Revenue, from annual notes)
    "materials_pct": [0.415,   0.403,   0.432,   0.451,   0.432],
    "employee_pct":  [0.078,   0.079,   0.077,   0.077,   0.078],
    "adspend_pct":   [0.108,   0.112,   0.109,   0.099,   0.102],
    "mfg_overhead_pct": [0.072, 0.071,  0.072,   0.073,   0.073],
    "royalty_pct":   [0.035,   0.035,   0.035,   0.035,   0.035],
    "other_opex_pct":[0.032,   0.034,   0.033,   0.030,   0.031],
}

# ---------------------------------------------------------------------------
# Commodity Exposure Weights within Materials Cost
# Based on HUL disclosures + category-level import analysis
# Palm oil is the key commodity shared across both segments
# ---------------------------------------------------------------------------

COMMODITY_WEIGHTS_WITHIN_MATERIALS = {
    # Commodity          HPC weight   BPC weight
    "Palm Oil & Derivatives": {
        "hpc": 0.32,   # surfactants, fatty acids → detergents, dishwash
        "bpc": 0.28,   # skin care base, soap noodles
    },
    "Petrochemicals / LAB": {
        "hpc": 0.18,   # linear alkylbenzene in detergents
        "bpc": 0.05,
    },
    "Packaging (Plastic/Laminate)": {
        "hpc": 0.20,
        "bpc": 0.22,
    },
    "Fragrance & Actives": {
        "hpc": 0.08,
        "bpc": 0.20,   # perfume, shampoo actives
    },
    "Other Agricultural Inputs": {
        "hpc": 0.12,
        "bpc": 0.15,
    },
    "Domestic Inputs (soda ash, NaOH, etc.)": {
        "hpc": 0.10,
        "bpc": 0.10,
    },
}

# ---------------------------------------------------------------------------
# 5-SKU Portfolio Definition
# Represents a representative Bangladesh-market FMCG range
# Import intensity = share of total COGS sourced in USD/hard currency
# ---------------------------------------------------------------------------

SKU_PORTFOLIO = [
    {
        "sku_id": "SKU-01",
        "name": "Premium Face Moisturiser",
        "segment": "BPC",
        "category": "Skin Care",
        "import_intensity": 0.72,   # 72% of COGS is USD-denominated imports
        "palm_oil_exposure": 0.28,   # palm-derived ingredients as % of COGS
        "base_asp_bdt": 850,         # average selling price per unit, BDT
        "base_gross_margin": 0.54,   # gross margin at base inputs
        "notes": "Premium end — imported actives, fragrance, packaging",
    },
    {
        "sku_id": "SKU-02",
        "name": "Anti-Dandruff Shampoo",
        "segment": "BPC",
        "category": "Hair Care",
        "import_intensity": 0.58,
        "palm_oil_exposure": 0.30,
        "base_asp_bdt": 320,
        "base_gross_margin": 0.48,
        "notes": "Mid-premium — SLES (palm-derived), ZPT active imported",
    },
    {
        "sku_id": "SKU-03",
        "name": "Bar Soap (Premium)",
        "segment": "BPC",
        "category": "Personal Wash",
        "import_intensity": 0.50,
        "palm_oil_exposure": 0.42,   # soap noodles are palm-derived
        "base_asp_bdt": 65,
        "base_gross_margin": 0.40,
        "notes": "High palm exposure via soap noodles; partial local production",
    },
    {
        "sku_id": "SKU-04",
        "name": "Liquid Dish Wash",
        "segment": "HPC",
        "category": "Home Care",
        "import_intensity": 0.38,
        "palm_oil_exposure": 0.35,
        "base_asp_bdt": 180,
        "base_gross_margin": 0.38,
        "notes": "Mid import intensity; surfactants from palm, rest domestic",
    },
    {
        "sku_id": "SKU-05",
        "name": "Fabric Wash Powder",
        "segment": "HPC",
        "category": "Laundry",
        "import_intensity": 0.28,    # lowest — large local soda ash usage
        "palm_oil_exposure": 0.22,
        "base_asp_bdt": 210,
        "base_gross_margin": 0.34,
        "notes": "Most domestic-input-heavy — soda ash, salt locally sourced",
    },
]


def build_hul_cost_structure_df() -> pd.DataFrame:
    df = pd.DataFrame(HUL_SEGMENT_DATA)

    # Derived columns
    df["hpc_ebit_margin"] = (df["hpc_ebit"] / df["hpc_revenue"]).round(4)
    df["bpc_ebit_margin"] = (df["bpc_ebit"] / df["bpc_revenue"]).round(4)
    df["blended_materials_pct"] = df["materials_pct"]

    # Gross margin proxy: net revenue less materials & mfg overhead
    df["implied_gross_margin"] = (
        1 - df["materials_pct"] - df["mfg_overhead_pct"]
    ).round(4)

    return df


def build_commodity_exposure_table() -> pd.DataFrame:
    rows = []
    for commodity, weights in COMMODITY_WEIGHTS_WITHIN_MATERIALS.items():
        rows.append({
            "Commodity": commodity,
            "HPC_Weight_In_Materials": weights["hpc"],
            "BPC_Weight_In_Materials": weights["bpc"],
            "Import_Denominated": commodity != "Domestic Inputs (soda ash, NaOH, etc.)",
        })
    return pd.DataFrame(rows)


def build_sku_df() -> pd.DataFrame:
    return pd.DataFrame(SKU_PORTFOLIO)


def compute_cogs_decomposition(sku_df: pd.DataFrame) -> pd.DataFrame:
    """
    For each SKU, decompose COGS (1 - gross margin) into:
      - Palm oil cost component (as % of revenue)
      - Other imported cost component
      - Domestic cost component
    """
    df = sku_df.copy()
    df["cogs_pct"] = 1 - df["base_gross_margin"]
    df["palm_oil_cogs_pct"] = df["palm_oil_exposure"]
    df["other_import_cogs_pct"] = (
        df["import_intensity"] - df["palm_oil_exposure"]
    ).clip(lower=0)
    df["domestic_cogs_pct"] = (
        df["cogs_pct"] - df["import_intensity"]
    ).clip(lower=0)

    # Cross-check: sum should approximate cogs_pct
    df["cogs_check"] = (
        df["palm_oil_cogs_pct"] +
        df["other_import_cogs_pct"] +
        df["domestic_cogs_pct"]
    ).round(4)

    return df


def compute_passthrough_analysis(
    sku_df: pd.DataFrame,
    palm_shock_pct: float = 0.30,       # +30% palm oil price shock
    fx_depreciation_pct: float = 0.10,  # +10% BDT/USD depreciation
) -> pd.DataFrame:
    """
    Compute gross margin impact under three pricing strategies:
      1. Zero pass-through  — full cost absorbed, no price increase
      2. Partial pass-through (50%) — half the cost increase passed to consumer
      3. Full pass-through — all cost increase passed to consumer

    Mechanics:
      - Palm oil shock affects palm_oil_cogs_pct directly
      - FX depreciation affects all import_intensity costs (palm oil + other imports)
      - Impact = cost increase as % of revenue base
    """
    results = []

    for _, sku in sku_df.iterrows():
        base_gm = sku["base_gross_margin"]
        cogs = 1 - base_gm

        # Palm oil: affected by both palm price shock AND FX depreciation
        palm_cost_base = sku["palm_oil_exposure"]
        palm_cost_shock = palm_cost_base * (1 + palm_shock_pct) * (1 + fx_depreciation_pct)
        palm_cost_increase = palm_cost_shock - palm_cost_base

        # Other imports: affected by FX depreciation only
        other_import_base = max(0, sku["import_intensity"] - sku["palm_oil_exposure"])
        other_import_shock = other_import_base * (1 + fx_depreciation_pct)
        other_import_increase = other_import_shock - other_import_base

        total_cost_increase = palm_cost_increase + other_import_increase

        results.append({
            "SKU_ID": sku["sku_id"],
            "SKU_Name": sku["name"],
            "Segment": sku["segment"],
            "Base_Gross_Margin_Pct": round(base_gm * 100, 1),
            "Palm_Cost_Increase_Pct_Revenue": round(palm_cost_increase * 100, 2),
            "FX_Import_Cost_Increase_Pct_Revenue": round(other_import_increase * 100, 2),
            "Total_Cost_Increase_Pct_Revenue": round(total_cost_increase * 100, 2),
            # Zero pass-through: GM absorbs full shock
            "GM_Zero_Passthrough": round((base_gm - total_cost_increase) * 100, 1),
            # Partial pass-through (50%): half the cost increase passed to consumer
            "GM_Partial_Passthrough_50pct": round(
                (base_gm - total_cost_increase * 0.50) * 100, 1
            ),
            # Full pass-through: price raised to restore base GM
            "GM_Full_Passthrough": round(base_gm * 100, 1),
            # Required price increase % to achieve full pass-through
            "Required_Price_Increase_Pct": round(
                (total_cost_increase / base_gm) * 100, 2
            ),
            "Palm_Shock_Applied": f"+{int(palm_shock_pct*100)}%",
            "FX_Depreciation_Applied": f"+{int(fx_depreciation_pct*100)}%",
        })

    return pd.DataFrame(results)


def main():
    print("=" * 60)
    print("  HUL COGS Decomposition — Bangladesh FMCG Proxy")
    print("=" * 60)

    df_hul = build_hul_cost_structure_df()
    df_commodities = build_commodity_exposure_table()
    df_skus = build_sku_df()
    df_cogs = compute_cogs_decomposition(df_skus)

    # Base scenario pass-through analysis
    df_analysis = compute_passthrough_analysis(
        df_cogs,
        palm_shock_pct=0.30,
        fx_depreciation_pct=0.10
    )

    print("\n--- HUL Blended Cost Structure (% of Net Revenue) ---")
    print(df_hul[[
        "fiscal_year", "materials_pct", "employee_pct",
        "adspend_pct", "mfg_overhead_pct", "implied_gross_margin"
    ]].to_string(index=False))

    print("\n--- Commodity Exposure Within Materials ---")
    print(df_commodities.to_string(index=False))

    print("\n--- SKU COGS Decomposition ---")
    print(df_cogs[[
        "sku_id", "name", "base_gross_margin",
        "palm_oil_cogs_pct", "other_import_cogs_pct", "domestic_cogs_pct"
    ]].to_string(index=False))

    print("\n--- Pass-Through Analysis (Palm +30%, BDT/USD +10%) ---")
    print(df_analysis[[
        "SKU_Name", "Base_Gross_Margin_Pct",
        "Total_Cost_Increase_Pct_Revenue",
        "GM_Zero_Passthrough", "GM_Partial_Passthrough_50pct",
        "GM_Full_Passthrough", "Required_Price_Increase_Pct"
    ]].to_string(index=False))

    # Exports
    df_hul.to_csv("hul_cost_structure.csv", index=False)
    df_commodities.to_csv("commodity_exposure_weights.csv", index=False)
    df_cogs.to_csv("sku_cogs_decomposition.csv", index=False)
    df_analysis.to_csv("passthrough_analysis_base.csv", index=False)

    # Also export SKU portfolio as JSON for dashboard consumption
    with open("sku_portfolio.json", "w") as f:
        json.dump(SKU_PORTFOLIO, f, indent=2)

    print("\n[OUTPUT] hul_cost_structure.csv")
    print("[OUTPUT] commodity_exposure_weights.csv")
    print("[OUTPUT] sku_cogs_decomposition.csv")
    print("[OUTPUT] passthrough_analysis_base.csv")
    print("[OUTPUT] sku_portfolio.json")
    print("\nDone.")


if __name__ == "__main__":
    main()
