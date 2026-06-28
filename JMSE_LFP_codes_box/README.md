# LFP_codes_box — MSEC 2026 Circularity Indicators (LFP)

Self-contained, shareable analysis package for the **LFP** (LiFePO₄) EV battery.
Computes five circularity indicators — **PCI, CI, CEI, ECPI** and the composite **M / R / E** —
from pre-generated input CSVs. Everything here runs as-is; no external data files needed.

Base case: **hydrothermal cathode route, 90 % collection efficiency.**

## Requirements
Python 3.12 with: `numpy`, `pandas`, `matplotlib`, `seaborn`, `openpyxl`, `SALib`
(`pip install numpy pandas matplotlib seaborn openpyxl SALib`).
Run with `MPLBACKEND=Agg` set, to avoid GUI windows blocking the scripts.

## Layout
```
Code/
  CEI/  CI/  ECPI/  PCI/  MRE/     each: <ind>_indicator.py + its parameter CSV (hydro + *_solid) + figures
  compiled_results_indicator.py    builds compiled_indicators_comparison_lfp.png from the cumulative CSV
  cumulative_results_indicators.csv   base-case (hydro, 90%) results — 7 indicators
  sensitivity/
     lfp_sensitivity_lite.py       self-contained S1/S2/S3 study runner (perturbs base CSVs, runs indicators)
     S1/S2/S3_sensitivity_study_lfp.xlsx + comparison PNGs + Raw_data_sensitivity_lfp.xlsx
  solid_state/                     solid-route outputs: cumulative_results_indicators_solid.csv,
                                   NMC811_vs_LFP_comparison_independent_lfp.png, lfp_bom_solid.json
Data Collection - Code/            reference data + provenance (NOT executed):
  lfp_greet_data.py                source-of-truth constants, every value provenance-tagged
  lfp_bom.json                     LFP bill-of-materials (606 kg pack)
  indicator_input_values_lfp.xlsx, indicator_inputs_variables_lfp.xlsx
  LFP_DATA_COLLECTION_AND_EXECUTION.md   full methodology + change log
```

## How to run

**1. Base case (hydrothermal) — five indicators + the compiled chart**
```bash
cd Code
for d in CEI/cei_indicator.py CI/ci_indicator.py ECPI/ecpi_indicator.py \
         PCI/pci_indicator_v2.py MRE/mre_indicator.py; do
  ( cd "$(dirname $d)" && python "$(basename $d)" )      # each updates ../cumulative_results_indicators.csv
done
python compiled_results_indicator.py                      # -> compiled_indicators_comparison_lfp.png
```

**2. Solid-state route** — one command (recommended), from `Code/solid_state/`:
```bash
cd Code/solid_state && python run_lfp_solid_independent.py
```
It runs the 5 indicators with `LFP_ROUTE=solid` (reading the included `*_solid.csv` inputs),
writes `cumulative_results_indicators_solid.csv` + the 3-way comparison figure
`NMC811_vs_LFP_comparison_independent_lfp.png`, and **never touches the hydro canon**.
Equivalently, run the 5 indicator scripts yourself with `LFP_ROUTE=solid` set
(PowerShell: `$env:LFP_ROUTE="solid"`), then unset it. *(Box edition: uses the included
`*_solid` CSVs — no GREET rebuild; the dev-repo runner rebuilds them via `build_lfp_inputs.py`.)*

**3. Sensitivity (S1 recycling-energy ±20 %, S2 recovery ±5 %, S3 collection 70/90/100 %)**
```bash
cd Code/sensitivity && python lfp_sensitivity_lite.py     # -> S1/S2/S3_*.xlsx + PNGs + Raw_data
```
`lfp_sensitivity_lite.py --restore-base` rebuilds the base cumulative + figures afterwards.

## Base-case results (hydro, 90 %)
| PCI | CI | CEI | ECPI | M | R | E |
|---|---|---|---|---|---|---|
| 0.240 | 0.373 | 0.418 | 0.092 | 0.584 | 0.619 | 0.651 |

Solid route differs only on **CI (0.350)** and **ECPI (0.066)** — cell-precursor energy and cathode GHG.
(ECPI revamped 2026-06-21: raw-input CSV + GHG/α/β computed inside `ecpi_indicator.py`, Cullen Eq.2 β = 0.8095 hydro.)

## Notes
- Iron & phosphorus are kept as inputs but **not recovered** (LFP hydromet → FePO₄/slag): recovery = 0
  across all indicators. See `LFP_DATA_COLLECTION_AND_EXECUTION.md` §14 (Iter 4–5).
- The data-generation scripts (`build_lfp_*.py`, GREET extraction) are **not bundled** — the input CSVs
  they produce are already included. `lfp_greet_data.py` is kept as the constants reference.
- `compute_ci_cullen` is inlined in `ci_indicator.py` (no shared module dependency).
