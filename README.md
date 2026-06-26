# Margin Resilience Simulator
### FMCG Input Cost Pass-Through Analysis Under BDT Depreciation & Commodity Shocks

[![Live Dashboard](https://img.shields.io/badge/Live%20Dashboard-View%20Interactive%20Tool-185FA5?style=for-the-badge)](https://ZibaMahdi.github.io/margin-resilience-simulator/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](python/)
[![Excel](https://img.shields.io/badge/Excel-Scenario%20Model-217346?style=flat&logo=microsoft-excel&logoColor=white)](excel/)

---

## What this project does

A three-layer scenario model that lets a commercial finance team stress-test 
gross margin impact of **simultaneous** BDT depreciation and palm oil price 
shocks across a representative Bangladesh-market FMCG portfolio (5 SKUs ranging 
from premium personal care to domestic-input-heavy home care).

**Core question answered:** *If palm oil moves X% and BDT depreciates Y%, 
what retail price increase is required to defend a target gross margin — 
and which SKUs breach the floor first?*

---

## Live dashboard

> **[→ Open the interactive scenario tool](https://ZibaMahdi.github.io/margin-resilience-simulator/)**

<img width="891" height="725" alt="Screenshot 2026-06-26 at 1 41 40 PM" src="https://github.com/user-attachments/assets/a60bad97-55fd-4b92-b700-63bcaa7964b7" />
<img width="843" height="312" alt="Screenshot 2026-06-26 at 1 42 10 PM" src="https://github.com/user-attachments/assets/faaa0d7c-0f3d-40e5-891f-99f88d772bc2" />
<img width="896" height="694" alt="Screenshot 2026-06-26 at 1 42 42 PM" src="https://github.com/user-attachments/assets/b36aefc7-3b0b-47f6-aad9-e0ce0e915aa3" />

Three views:
- **Scenario engine** — live sliders for palm shock, BDT/USD depreciation, 
  GM floor target, and pass-through strategy; SKU cards update in real time
- **Margin waterfall** — profit erosion decomposed by shock source 
  (palm oil vs FX import costs)
- **Historical context** — palm oil price vs BDT/USD time series 
  (Jan 2019 – Dec 2024) and HUL materials % vs implied GM

---

## Data sources

| Source | Series | Use in model |
|---|---|---|
| [World Bank Pink Sheet](https://www.worldbank.org/en/research/commodity-markets) | Palm oil USD/MT, monthly Jan 2019–Dec 2024 | Commodity shock axis |
| [Bangladesh Bank](https://www.bb.org.bd/en/index.php/econdata/exchangerate) | BDT/USD mid-rate, monthly | FX depreciation axis |
| [HUL Annual Reports (NSE/BSE)](https://www.hul.co.in/investor-relations/annual-reports/) | Segment financials FY2020–FY2024, Home Care & BPC | COGS decomposition structural proxy |

**Why HUL as proxy:** Unilever Bangladesh does not file segment-level cost 
disclosures. HUL operates the same Unilever global portfolio taxonomy and 
commodity input set; regional finance teams benchmark against HUL segment 
economics. The proxy is structural, not aspirational.

---

## Three-layer methodology

### Layer 1 — COGS decomposition
HUL's disclosed cost structure (materials, employee, ad-spend, manufacturing 
overhead, royalty) mapped to Bangladesh FMCG unit economics. Commodity exposure 
weights calibrated within the materials line: palm oil & derivatives, 
petrochemicals/LAB, packaging, fragrance & actives, domestic inputs.

### Layer 2 — Sensitivity engine (Excel)
2-D matrix for each of 5 SKUs:
- **Rows:** Palm oil price shock (−20% to +50% in 10pp steps)
- **Columns:** BDT/USD depreciation (0% to +30% in 5pp steps)
- **Three sub-tables per SKU:** zero pass-through / 50% pass-through / full pass-through
- **Companion table:** required retail price increase to defend base gross margin




### Layer 3 — Interactive dashboard
Slider-driven tool showing GM outcomes and required pricing actions in real time.
Built in vanilla JS + Chart.js. [Live here →](https://ZibaMahdi.github.io/margin-resilience-simulator/)

---

## 5-SKU portfolio

| SKU | Product | Segment | Import Intensity | Palm Exposure | Base GM |
|---|---|---|---|---|---|
| SKU-01 | Premium Face Moisturiser | BPC | 72% | 28% | 54% |
| SKU-02 | Anti-Dandruff Shampoo | BPC | 58% | 30% | 48% |
| SKU-03 | Bar Soap (Premium) | BPC | 50% | 42% | 40% |
| SKU-04 | Liquid Dish Wash | HPC | 38% | 35% | 38% |
| SKU-05 | Fabric Wash Powder | HPC | 28% | 22% | 34% |

---

## Key findings

**1. Bar Soap (SKU-03) is the highest-risk SKU.** Under Palm +30% / BDT −10% 
with zero pass-through, GM collapses from 40% → 21% — the steepest erosion in 
the portfolio. A 47% retail price increase would be required for full 
pass-through. Palm exposure (42% of COGS) drives the vulnerability.

**2. Fabric Wash Powder (SKU-05) is the most resilient.** Lowest import 
intensity (28%) and palm exposure (22%) limits GM erosion to ~10pp under the 
same shock vs ~19pp for Bar Soap. Domestic soda ash/NaOH inputs provide a 
natural FX hedge.

**3. 50% pass-through is the viable middle path.** Across all 5 SKUs, a 50% 
pass-through under the base shock (Palm +30%, FX +10%) keeps all GMs above 29% 
— above the 30% management floor for 4 of 5 SKUs. Full pass-through on Bar 
Soap specifically is required to avoid a floor breach.

**4. Shock sequencing is non-linear.** A +20% BDT depreciation layered on top 
of Palm +30% increases the required price move by 8–12pp vs the FX-only shock 
— because FX amplifies the palm cost in BDT terms simultaneously.

---

## Executive summary

<img width="1072" height="601" alt="docs:screenshots:slide1" src="https://github.com/user-attachments/assets/672f16e3-a586-44c5-8e84-5a7f4426d34f" />
<img width="1079" height="582" alt="docs:screenshots:slide2" src="https://github.com/user-attachments/assets/fe52fea5-9ae4-47c6-a410-24552e0685b1" />



[Download PPTX →](https://github.com/ZibaMahdi/margin-resilience-simulator/raw/main/presentation/Margin_Resilience_Simulator_Mgmt_Presentation.pptx)


---

## Excel model

Three-tab model with colour-coded inputs (blue), formulas (black), 
and cross-sheet links (green) — standard commercial finance convention.

<img width="1438" height="469" alt="docs:screenshots:excel_cogs" src="https://github.com/user-attachments/assets/69d449dc-4af1-48fb-aae3-434219a20752" />
<img width="1008" height="470" alt="docs:screenshots:excel_peer" src="https://github.com/user-attachments/assets/c6f1ed9d-31c5-4e5e-aeb4-aea5fee17f27" />
<img width="1049" height="618" alt="Screenshot 2026-06-26 at 1 53 09 PM" src="https://github.com/user-attachments/assets/9c183fee-3372-478b-b663-e6197d769b99" />



[Download Excel model →](https://github.com/ZibaMahdi/margin-resilience-simulator/raw/main/excel/Margin_Resilience_Simulator.xlsx)


---

## Python scripts

| Script | Purpose |
|---|---|
| `01_worldbank_palmoil.py` | Pink Sheet palm oil series extraction, cleaning, YoY/rolling averages, shock scenario table |
| `02_bangladeshbank_fx.py` | BDT/USD series, depreciation categorisation, import cost multiplier grid |
| `03_hul_cogs_decomposition.py` | HUL cost structure decomposition, SKU portfolio definition, pass-through analysis engine |

All scripts run with embedded historical data by default. 
Pass `--live` flag to attempt live API/scrape fetch.

```bash
pip install pandas openpyxl requests beautifulsoup4
python python/01_worldbank_palmoil.py
python python/02_bangladeshbank_fx.py
python python/03_hul_cogs_decomposition.py
```

---



*Data: World Bank Pink Sheet · Bangladesh Bank · HUL Annual Reports (NSE/BSE)*
*Tools: Python · Excel · Chart.js · GitHub Pages*
