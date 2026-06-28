# LFP Circularity-Indicator Analysis — Data Collection & Execution

**Project:** MSEC '26 — battery circularity indicators
**Chemistry:** LFP (LiFePO₄), EV 300-mile pack
**Reference chemistry:** NMC811 (this study mirrors the NMC811 pipeline)
**Base case:** Hydrothermal cathode route, 90 % collection efficiency
**Date built:** 2026-06-15
**Working directory:** `E:\ARPA-E\MSEC_2026\LFP\`

---

## 1. Scope and approach

This study computes seven circularity indicators for an LFP EV battery:

| Indicator | Name | Reference |
|---|---|---|
| **PCI** | Product Circularity Indicator | Bracquené et al. / Picatoste 2024 |
| **CI** | Circularity Index (energy/quality) | Cullen 2017 |
| **CEI** | Circular Economy Index (economic) | Di Maio & Rem 2015 |
| **ECPI** | Eco-Circularity Performance Index | Carmona-Aparicio 2025 |
| **M / R / E** | Material / Recovery / Energy composite | Bin 2025 (SPC) |

The whole pipeline is **driven by a GREET-derived bill-of-materials (BOM)** plus a
GREET energy/GHG inventory. The LFP version mirrors the committed NMC811 analysis
(`E:\ARPA-E\MSEC_2026\{cei,ci,ecpi,mre,pci}\`) but with LFP chemistry and **all
energy/GHG values recomputed from GREET** (nothing carried over from NMC811 except
documented methodology assumptions — see §8).

Pipeline shape: each indicator script reads a parameter CSV → runs a 1000-sample
Monte-Carlo → appends `(mean, CI_lower, CI_upper)` to
`cumulative_results_indicators.csv` and writes plots.

---

## 2. Data sources

### 2.1 Primary — R&D GREET 2024 Rev1
`Literature/NMC811/RD GREET2024_Rev1/R&D GREET2024_Rev1/R&D GREET2_2024_Rev1.xlsm`
(battery module is in GREET **2**). Read headlessly with
`openpyxl(..., data_only=True, read_only=True)`. **The GREET VBA macros cannot be
run headlessly**, but all LFP data needed is available in *static per-chemistry
tables*, so no recalculation was required.

| Data | GREET location |
|---|---|
| Battery composition (% mass, per chemistry × EV range) | `Battery_Sum` §7, rows 638+ |
| Specific energy per chemistry | `Battery_Sum` §8 (LFP 142.89, NMC811 197.69 Wh/kg) |
| Cathode material use (recipe, ton/ton) | `Battery_Sum` §9.2 / `Other_Cathodes` |
| Cathode production energy & emissions | `Battery_Sum` §9.4 (hydro & solid columns) |
| Precursor production intensities (LiOH, H₃PO₄, FeSO₄…) | `Other_Cathodes` cathode-precursor block (rows 151/153/170) |
| Per-material energy & GHG intensities (graphite, Cu, Al, steel, electrolyte…) | `NMC811_Compiled_MSEC.xlsx` "Greet 2024" §4.3 Li-Ion (mmBtu/lb, g/lb) |
| Battery assembly energy | `Battery_Assembly` (0.200 mmBtu/kWh) |
| Recycling recovery (process yields, per chemistry incl. LFP) | `Battery Recycling` sheet |

### 2.2 Literature / market data
- **Prices:** `Literature/Price information/Price Analysis for Battery-Relevant Materials (Virgin vs. Recycled).docx` + USGS MCS 2024/2025 + Argonne EverBatt.
- **Recovery efficiencies:** GREET `Battery Recycling` (cross-check) + FHanna 2025 (EST) + EverBatt.

---

## 3. Bill of materials (BOM)

**Pack basis (constant pack energy):** the LFP pack delivers the same ~86.6 kWh as
the NMC811 reference but is heavier because LFP specific energy is lower:

```
PACK_LFP = 438.235 kg × (197.69 / 142.89)  =  606.3 kg
```

**Material masses** = GREET composition fraction (EV 300-mile, LFP) × 606.3 kg.
The active material (LiFePO₄, 27.59 % = 167.3 kg) is decomposed elementally
(LiFePO₄ molar mass 157.76 g/mol):

| Material | Mass (kg) | Source |
|---|---|---|
| Pack (total) | 606.3 | GREET specific energy |
| Active LiFePO₄ | 167.3 | GREET 27.59 % |
| → lithium | 7.36 | LiFePO₄ × 4.40 % |
| → iron (cathode) | 59.22 | LiFePO₄ × 35.40 % |
| → phosphorus | 32.84 | LiFePO₄ × 19.63 % |
| → oxygen (untracked) | 67.86 | LiFePO₄ × 40.57 % |
| copper | 61.36 | GREET 10.12 % |
| aluminium (wrought) | 75.85 | GREET 12.51 % (recyclable subset 59.28) |
| steel + stainless | 118.59 | GREET 13.73 % + 5.83 % |
| graphite | 85.97 | GREET 14.18 % |
| cell mass | 402.95 | Σ LFP cell components (OWinjobi 2020) — Iter-3 fix |

**Key chemistry change vs NMC811:** LFP cathode has **no Ni, Co, or Mn**; iron and
phosphorus are new tracked materials. Indicator material lists drop Co/Ni/Mn and add
Fe/P.

Implemented in `build_lfp_inputs.py`; values cached to `lfp_bom.json`.

### 3.1 Exact GREET cell provenance — where battchem, range & kg were selected

**battchem + range together pin down a single column: V** (LFP Hydrothermal inside the
300-mile block). The composition `COMP` dict in `lfp_greet_data.py:29-39` is column **V,
rows 639–658**. Verified: **V639 (Active Material) = 0.2759** — exactly the
`active_material` value in the code (the 150-mile value in col D was 0.2491; you'd have
read the wrong number if the range weren't fixed to 300). In `Battery_Sum §7` the range
header (row 637) lays out four blocks — 150 mi (B–J), 200 mi (K–S), **300 mi (T–AB)**,
400 mi (AC–AK) — and within the 300-mile block the chemistry header (row 638) puts LFP
(Hydrothermal) at **column V**.

**Specific energy** comes from `Battery_Sum §8` ("Specific energy dependency on EV range
and chemistry"), **row 664 = "EV: 300 Miles"**:
- **D664 = 142.89 Wh/kg** (LFP) → `LFP_SE_WHKG`
- **G664 = 197.69 Wh/kg** (NMC811) → `NMC_SE_WHKG`

(`lfp_greet_data.py:20-21`)

**kg → derived, not read from a GREET cell.** There is no GREET pack-mass cell for the LFP
pack. The mass basis is computed in `lfp_greet_data.py:19-23` by holding pack energy
constant to the NMC811 reference:

```
PACK_ENERGY_KWH = 438.235 kg × 197.69 Wh/kg / 1000  ≈ 86.6 kWh   (NMC811 reference)
PACK_KG (LFP)   = 86.6 kWh × 1000 / 142.89 Wh/kg     ≈ 606.30 kg
```

That **606.30 kg** is the `TOTAL_BATTERY_MASS` row in `pci_material_parameters.csv`. Each
material kg = composition % (column V) × 606.30, done at `build_lfp_inputs.py:27`, then
mapped into PCI's `M` column (`build_lfp_inputs.py:103-110`).

---

## 4. Energy & GHG inventory (GREET-derived)

All energy/GHG is computed from GREET intensities — **no NMC carry-over**.

### 4.1 Chemistry-independent materials
Per-material intensities (GREET §4.3 Li-Ion, mmBtu/lb energy, g/lb GHG) are the same
for any cathode (copper production energy is copper production energy). Converted via
1 mmBtu = 1055.06 MJ, 1 lb = 0.453592 kg.

### 4.2 LFP active material (cathode), cradle-to-gate
Built from the GREET cathode recipe × precursor intensities + synthesis:

| Precursor | ton/ton LiFePO₄ | Energy (mmBtu/ton) | GHG (t CO₂/ton) | GREET source |
|---|---|---|---|---|
| LiOH | 0.26838 | 248.90 | 20.539 | `Other_Cathodes` col 16 |
| H₃PO₄ | 0.36606 | 14.625 | 0.965 | `Other_Cathodes` col 18 |
| FeSO₄ | 0.56745 | 0 (byproduct) | 0 | `Other_Cathodes` col 19 |
| NMP | 0.007 | 328.77 | ~18 | `Battery_Materials` |
| **Synthesis (hydro)** | — | 34.217 | 1.989 | `Battery_Sum` §9.4 |

**Result (hydrothermal):** active LiFePO₄ = **108.7 mmBtu/ton, 7.98 t CO₂/ton**
(vs NMC811 active material 307.8 mmBtu/ton — LFP is ~⅓ the embodied energy).
Solid-state route (Li₂CO₃ + Fe₃O₄ + DAP + synthesis 4.97 mmBtu/ton) ≈ 33.7 mmBtu/ton.

### 4.3 Battery-level totals (LFP, hydro)

| Quantity | LFP value | NMC811 (was) |
|---|---|---|
| Material processing energy | 50,582 MJ | 61,193 |
| Assembly energy | 18,285 MJ | 18,281 |
| **Total production energy** (E_total_2 / QP_ipf) | **68,868 MJ** | 79,474 |
| Production GHG (materials) | 3,529 kg CO₂e | — |
| Total GHG (incl. assembly) | 4,610 kg CO₂e | — |

These feed the MRE **E-block** (`E_processing`, `E_assembly`, `E_total_2`, `QP_ipf`,
`E_recovery`, `E_pre_treatment`).

---

## 5. Recovery efficiencies & prices

### 5.1 Recovery efficiency (material efficiency) — verified
| Material | η | Source / tag |
|---|---|---|
| lithium | 0.90 | GREET Battery Recycling hydromet Li₂CO₃ yield; FHanna ≈0.90 `[GREET-LFP/LIT]` |
| copper | 0.96 | GREET/EverBatt Cu collector `[GREET-GEN/LIT]` |
| aluminium | 0.93 | EverBatt (module+pack) `[GREET-GEN/LIT]` |
| steel | 0.95 | ferrous scrap, standard `[LIT]` |
| graphite | 0.90 | GREET Battery Recycling hydromet graphite (LFP) `[GREET-LFP]` |
| iron | **0.00** | Fe → FePO₄/slag, **not recovered** `[DECISION 2026-06-19]` (see §14 Iter-4) |
| phosphorus | **0.00** | P → FePO₄/slag, **not recovered** `[DECISION 2026-06-19]` (see §14 Iter-4) |

### 5.2 Prices ($/kg, virgin / recycled)
Al 3.30/1.12 · Cu 8.80/7.11 · Li 30.0/8.37 · steel 1.00/0.33 `[LIT]`;
iron 1.00/0.30 · phosphorus 2.50/1.00 `[LIT-EST]`.

All defined in `lfp_greet_data.py` with inline source tags.

---

## 6. Indicator methodology (how each uses the data)

- **CEI** (economic): `Σ(mass_recycled·price_recycled) / Σ(mass_required·price_virgin)`.
  `mass_recycled = mass · η · collection`. Materials: Al, Cu, Fe, Li, P, steel.
- **PCI**: per-material circularity from process parameters (F_r=η, C_r=collection,
  E_cp/E_fp efficiencies…), mass-weighted to a final EVB PCI.
- **CI** (Cullen): pack steel + aluminium + cell. Cell = cathode precursors (LiOH,
  H₃PO₄, FeSO₄) + cell Al + cell Cu (**no graphite**); the Fe/P precursors (FeSO₄, H₃PO₄)
  have **recovery_rate = 0**. α = recovered/mass, β = 1 − recycling-energy/virgin-energy.
- **ECPI** (revamp 2026-06-21): input CSV holds only raw per-material inputs; all GHG/α/β
  math is in `ecpi_indicator.py` (`compute_ecpi`, default `mode='eq2'`). β = 1 −
  circular/linear over the **recovered** materials {LiOH,Cu,Al,steel} (Cullen Eq. 2; Fe/P
  excluded from both sides — they only dilute α). α carries quantity (recovered mass ×
  collection × F_r). Hydro: circular 513.78, linear 2696.94, β 0.8095, α 0.11, ECPI 0.092.
- **M / R / E**:
  - **M** (material): M1 recycled-input content, M2 recovery importance, M3 recovery
    potential (η), M4 regional, M5 cost, M6 water, M7 waste — mass/recovery-driven
    (LFP-specific).
  - **R** (recovery): R1 manufacturing efficiency, R2 reuse, R3 repurpose, R4
    qualitative — ratio-based + scenario assumptions.
  - **E** (energy): E1 renewable share, E2 energy-saving, E3 lifecycle energy
    (now GREET-LFP), E4 functional energy. **Fraction-dominated → numerically stable.**

---

## 7. Cathode synthesis route (Hydrothermal vs Solid-State)
Route affects **only** CI (active-material energy) and ECPI (cathode GHG). PCI, CEI,
M, R, E are route-independent. Set with `LFP_ROUTE=hydro|solid`.

---

## 8. Provenance & carry-over audit

Full audit in `indicator_inputs_variables.xlsx → CARRY_OVER_AUDIT`. Summary:

| Status | Items |
|---|---|
| ✅ **GREET-LFP** | composition, masses, pack, specific energy, cathode recipe + production energy/GHG, MRE E_processing/E_total/QP_ipf/E_assembly |
| ✅ **GREET-GEN** (chemistry-independent, correct to reuse) | per-material energy/GHG intensities, assembly energy |
| ✅ **GREET-LFP** | MRE E_recovery / E_pre_treatment (direct from GREET Battery Recycling sheet, LFP + hydromet — as of 2026-06-20; no longer production-ratio-scaled) |
| 🟢 **LIT** (cited) | recovery efficiencies (Li/Cu/Al/steel/graphite), prices (Al/Cu/Li/steel) |
| 🟠 **LIT-EST** (flagged) | iron & phosphorus recovery + price (FePO₄ co-recovery) |
| 🔴 **ASSUMP carried** (methodology, *not* chemistry-specific) | MRE E1/E2 weights, E4 conversion factors, M4 regional masses, M6/M7 water/waste fractions, R2/R3 second-life splits, R4 qualitative scores Q1–Q9, sub-index weights n*/r*/e* |

The 🔴 items are LCA *methodology/scenario* choices (renewable-energy mix, second-life
pathways, expert design scores). They are not derivable from GREET; revise them in
`mre/mre_indicator.csv` if LFP-specific scenarios are desired.

---

## 9. Execution

### 9.1 Requirements
Python 3.12, `openpyxl`, `pandas`, `numpy`, `matplotlib`, `seaborn`, `SALib`
(`pip install SALib`). Run with `MPLBACKEND=Agg` to avoid GUI blocking.
The CI script is self-contained — `compute_ci_cullen` is inlined in `ci_indicator.py`
(no `Code Shared AL` dependency).

### 9.2 Environment-variable knobs
| Var | Default | Effect |
|---|---|---|
| `LFP_COLLECTION` | 0.90 | collection efficiency (S3: 0.70/0.90/1.00) |
| `LFP_ROUTE` | hydro | cathode route (hydro/solid) |
| `LFP_RECOVERY_MULT` | 1.0 | recovery-efficiency multiplier (S2: ±5 %) |
| `LFP_RECYC_MULT` | 1.0 | recycling-energy multiplier (S1: ±20 %) |

### 9.3 Build order
```bash
cd E:\ARPA-E\MSEC_2026\LFP
# 1. base-case parameter CSVs + energy inventory
python build_lfp_inputs.py        # -> cei/ci/pci/ecpi CSVs + lfp_bom.json
python build_lfp_mre.py           # -> mre/mre_indicator.csv (GREET E-block)
# 2. collection sweep -> cumulative_results_indicators.csv + Cumulative table
python run_lfp_sweep.py
# 3. solid-state + 3-way comparison figure (independent: writes only *_solid, hydro canon untouched)
python run_lfp_solid_independent.py   # NOT the old run_lfp_solid.py (deprecated toggle-and-restore)
# 4. sensitivity studies S1/S2/S3 + Raw_data_sensitivity + PNGs
python build_lfp_sensitivity.py
# 5. documentation workbooks
python build_lfp_workbooks.py
```
Each indicator script may also be run standalone from its own folder
(`cd pci && python pci_indicator_v2.py`).

### 9.4 Source-of-truth module
`lfp_greet_data.py` holds **every** constant with a provenance tag — edit here to
revise inputs; all build scripts import from it.

---

## 10. Outputs

All deliverables are suffixed **`_lfp`** so they can be opened side-by-side with the
NMC811 originals.

| File | Contents |
|---|---|
| `cumulative_results_indicators_lfp.csv` | base case (hydro, 90 %): 7 indicators (working copy: `cumulative_results_indicators.csv`) |
| `cumulative_results_solidstate_lfp.csv` | solid-state base case |
| `Cumulative_ECPI_CEI_MRE_Table_lfp.xlsx` | collection sweep 70/90/100 % |
| `indicator_input_values_lfp.xlsx` | **NMC811-format** sheets (PCI_inputs / CI_inputs / CEI_inputs / ECPI_indicator / MRE_indicator): BOM (lb/kg) left, M-block + LiFePO₄ decomposition, parameter table + **Reference column**, References block |
| `indicator_inputs_variables_lfp.xlsx` | ALL_INPUTS, **CARRY_OVER_AUDIT**, LEGEND |
| `S1/S2/S3_sensitivity_study_lfp.xlsx` | study tables |
| `Raw_data_sensitivity_lfp.xlsx` | all three studies (3 sheets) |
| `S1/S2/S3_sensitivity_scenarios_comparison_lfp.png` | grouped bar charts |
| `NMC811_vs_LFP_comparison_lfp.png` | NMC811 vs LFP-hydro vs LFP-solid |
| `compiled_indicators_comparison_lfp.png` | base-case bar chart |
| per-indicator `*.png` in `cei/ci/ecpi/mre/pci/` | bar/tornado/error-bar plots |

---

## 11. Results  *(current as of the 2026-06-20 Iter-5 MRE-correction update — see §14 change log)*

### 11.1 Base case (hydrothermal, 90 % collection) — Iter 6 (ECPI revamp 2026-06-21)
| PCI | CI | CEI | ECPI | M | R | E |
|---|---|---|---|---|---|---|
| 0.240 | 0.373 | 0.418 | **0.092** | 0.584 | 0.619 | 0.651 |

*(Iter-4 M/R/E were 0.605 / 0.620 / 0.638 before the 2026-06-20 MRE energy/mass/cost correction;
PCI/CI/CEI/ECPI unchanged from Iter-4. Iter-3 values, before Fe/P-recovery=0:
PCI 0.409 · CI 0.605 · CEI 0.450 · ECPI 0.178/0.224 · M 0.629.)*

### 11.2 NMC811 vs LFP routes (90 % collection)
*(All three columns current as of 2026-06-20. LFP-Solid generated by
`run_lfp_solid_independent.py` — writes only `*_solid` files; hydro canon verified byte-identical.)*
| Indicator | NMC811 | LFP-Hydro | LFP-Solid |
|---|---|---|---|
| PCI | 0.398 | 0.240 | 0.240 |
| CI | 0.582 | 0.373 | **0.349** |
| CEI | 0.569 | 0.419 | 0.418 |
| ECPI | 0.122 | **0.092** | **0.066** |
| M | 0.613 | 0.585 | 0.578 |
| R | 0.620 | 0.619 | 0.619 |
| E | 0.638 | 0.651 | 0.651 |

*(NMC811 column = `JMSE_NMC811_codes_box` reference cumulative.)*

### 11.3 Collection sweep (S3) — Iter 6
| Coll % | PCI | ECPI | CEI | M | R | E |
|---|---|---|---|---|---|---|
| 70 | 0.147 | 0.071 | 0.326 | 0.575 | 0.618 | 0.651 |
| 90 | 0.239 | 0.092 | 0.419 | 0.584 | 0.619 | 0.651 |
| 100 | 0.276 | 0.102 | 0.465 | 0.589 | 0.620 | 0.651 |

### 11.4 S1 — recycling energy ±20 % → CI, E *(Iter 5)*
CI 0.350 / 0.372 / 0.395 (+20/0/−20 %); E 0.650 / 0.651 / 0.652.

### 11.5 S2 — recovery efficiency ±5 % → PCI, CI, CEI, ECPI, M *(Iter 6 — ECPI now responds to recovery)*
PCI 0.246/0.239/0.230 · CI 0.387/0.373/0.356 · CEI 0.436/0.419/0.397 · ECPI 0.096/0.092/0.088 · M 0.586/0.584/0.581 (+5/0/−5 %).

### 11.6 Hydrothermal vs Solid-State (route dependence)
*(also in `indicator_input_values_lfp.xlsx` → `Hydro_vs_Solid` sheet)*

| Indicator | LFP-Hydro (Iter 5) | LFP-Solid | Route-dependent? |
|---|---|---|---|
| PCI | 0.240 | 0.240 | No |
| CI | 0.373 | **0.349** | **Yes** (the meaningful one) |
| CEI | 0.419 | 0.418 | No |
| ECPI | 0.092 | **0.066** | **Yes** (β 0.8095 → 0.760) |
| M | 0.585 | 0.578 | No (≈, MC noise) |
| R | 0.619 | 0.619 | No |
| E | 0.651 | 0.651 | No |

*(LFP-Solid generated 2026-06-20 by `run_lfp_solid_independent.py`; route moves only **CI** (cell
precursor energy: Li₂CO₃/Fe₃O₄/DAP vs LiOH/H₃PO₄/FeSO₄) and **ECPI** (cathode synthesis GHG).)*

Only **CI** (clearly), **ECPI** (slightly), and **E** (marginally) change with route. Why:
- **CI** — cell-level energy differs: hydro precursors LiOH/H₃PO₄/FeSO₄ vs solid
  Li₂CO₃/Fe₃O₄/DAP, plus cathode synthesis 34.2 vs 4.97 mmBtu/ton.
- **ECPI** — cathode GHG / lithium precursor differs.
- **E** — active-material energy feeds `E_processing` (but E is fraction-dominated, so it
  barely moves).
- **PCI, CEI, M, R** are driven by mass, price, and recovery, which are identical for both
  routes (LFP composition is the same; only the cathode-production LCA differs) — so they
  are route-independent by construction.

---

## 12. Key findings & interpretation *(Iter 5 — Fe/P treated as produced-but-not-recovered)*
- **PCI falls** (0.398 → 0.240): iron & phosphorus are large cathode masses that are
  **produced but not recovered** in LFP hydromet (→ FePO₄/slag), so they carry mass weight
  with zero recovery credit.
- **CI falls** (0.582 → 0.373): the FeSO₄/H₃PO₄ cell precursors are no longer credited as
  recovered (recovery_rate = 0), which lowers the cell mass-circularity α. (The energy-β is
  still favourable — LFP cell recycling is only 6.35 vs 27.5 mmBtu/ton — but α dominates.)
- **CEI falls** (0.569 → 0.419): recovered LFP materials carry little economic value, and Fe/P
  now contribute **zero** recovered value (mass_recycled = 0) — the central LFP recycling story.
- **ECPI falls** (0.122 → 0.092): with the Cullen Eq.2 β method (β = 0.8095, *higher* than
  NMC's), the low ECPI is **α-driven** — Fe/P are produced but not recovered, so their
  unrecovered mass enters the α denominator (α ≈ 0.11) while β stays high.
- **M falls slightly** (0.613 → 0.585) with Fe/P recovery removed; **R ≈ 0.619** flat.
- **E rises** (0.637 → 0.651): the corrected GREET-LFP recycling energy (E_recovery
  1547 MJ, vs the old 6705) makes the end-of-life energy far lighter → higher energy circularity.
- **Route effect** isolated to CI (cell energy) and ECPI (cathode GHG).

---

## 13. Limitations / to-revise
1. **Iron & phosphorus** recovery/price/GHG are literature estimates (`LIT-EST`).
2. **🔴 carried-over methodology assumptions** (§8) are not chemistry-specific —
   supply LFP-specific second-life pathways / qualitative scores to refine M/R/E.
3. GREET `Battery Recycling` is process-yield based; recovery efficiencies were
   cross-checked but not mechanically mapped 1:1.
4. Monte-Carlo CIs use ±5 % parameter uncertainty (per the NMC811 convention).

---

## 14. Change log

### Iteration 6 — 2026-06-21 (ECPI revamp: raw-input CSV + Cullen Eq.2 β)

ECPI moved to a **raw-input CSV** — `ecpi/ECPI_indicator_alpha_sum.csv` now holds only
per-material `mass_recover / mass_prod / virgin_ghg / F_r / in_circ / cell_frac /
recycled_ghg_direct / fr_on_direct` + `PARAM_collection / cell_recycling_ghg_per_kg /
cell_mass_kg`; **all GHG/α/β math moved into `ecpi/ecpi_indicator.py`** (`compute_ecpi`,
default `mode='eq2'`).
- **β = Cullen Eq. 2** over the recovered materials {LiOH,Cu,Al,steel} only; Fe/P excluded
  from both sides (they only dilute α). Circular = recycled-credit GHG 513.78 (cell 317.94 +
  pack-Al 122.82 + steel 73.02); linear 2696.94 → **β 0.8095** (hydro), 0.760 (solid).
- **α** carries quantity: α_out = Σ(mass·collection·F_r)/Σmass; Fe/P (F_r 0) dilute it → α 0.11.
- F_r **standardized**: Li 0.90 → **0.91** (Cu 0.96, Al 0.93, steel 0.95) in `lfp_greet_data.py`;
  all 5 indicator CSVs regenerated.

**Effect:** ECPI 0.095 → **0.092** (hydro), 0.064 → **0.066** (solid). PCI/CI/CEI/M/R/E unchanged.
**Sensitivity:** `lfp_sensitivity_lite.py` `t_ecpi()` rewritten for the raw schema; **ECPI now
reported in S2 (recovery) as well as S3 (collection)**. `LFP_codes_box/` regenerated + smoke-tested
(hydro + solid + lite all run from the box; build/orchestrator scripts removed for a lean shareable box).

### Iteration 5 — 2026-06-20 (MRE input correction: LFP-native energy / mass / cost)

Full detail in **`MRE_LFP_corrections_2026-06-20.md`**. Replaced every NMC811-carried,
chemistry/pack-specific MRE value with an LFP-native / GREET-LFP / EverBatt-LFP value:
- **Recycling energy** (the big one): `E_recovery` 6705 → **1547 MJ**, `E_pre_treatment`
  → **1430 MJ** — now read directly from GREET "Battery Recycling" (LFP + hydromet:
  recycling 24.46 → 3.30 mmBtu/ton cells; no Co/Ni to recover), no longer production-ratio-scaled.
- **Material masses & η** reconciled to the ECPI feedstock basis; cathode Fe/P `eta_hydro = 0`
  (consistent with Iter-4); `m_re_total` 84.68 → **92.88**, `m_vir_total` → **363.97**.
- **M5 cost** from EverBatt 2023 (`C_total` 29.77 → **20.33** $/kg cell, `C_labor` → 0.44).
- **Lifetimes:** primary service life 8 → **12 yr**; second-life durations unified to 5 yr.

**Effect on M/R/E (base case):** M 0.605 → **0.585**, R 0.620 → **0.619**, E 0.638 → **0.651**.
PCI/CI/CEI/ECPI unchanged from Iter-4 (0.240 / 0.373 / 0.419 / 0.095).

The base cumulative and the **S1/S2/S3 sensitivity studies were regenerated** with
`lfp_sensitivity_lite.py` — a self-contained runner that perturbs the base CSVs and runs only
the five indicator scripts (no `build_lfp_inputs` re-derivation; validated against the
orchestrator to ≤0.0015).

**Solid-state route + NMC-vs-LFP comparison regenerated 2026-06-20** with the new
`run_lfp_solid_independent.py` (writes only `*_solid` files; hydro canon verified byte-identical
by sha256 — supersedes the old toggle-and-restore `run_lfp_solid.py`). Solid base case
(90 % collection): **PCI 0.240 · CI 0.349 · CEI 0.418 · ECPI 0.064 (β 0.700) · M 0.578 · R 0.619 · E 0.651**.

### Iteration 4 — 2026-06-19 (iron & phosphorus: produced but not recovered)

**Decision:** iron and phosphorus are kept as **inputs** in every indicator but their
**recovery is set to 0** (LFP hydromet sends Fe/P to FePO₄/slag — not recovered).
Full discussion + tables in **`IRON_PHOSPHORUS_TREATMENT.md`**; the ECPI-circular /
β-principle analysis in **`ECPI_CIRCULAR_AND_BETA_METHODOLOGY.md`**.

Changes (central knob `lfp_greet_data.py` `RECOVERY['iron'/'phosphorus']` eta → 0):
- **CEI** iron/phosphorus `mass_recycled = 0`
- **PCI** iron/phosphorus `F_r = 0`
- **CI** `cell_material_FeSO4`/`H3PO4` `recovery_rate = 0` (mass + energy_virgin kept)
- **MRE** Iron/Phosphorus `eta_hydro = 0`
- **ECPI** added FeSO₄ & H₃PO₄ rows: m_in_circular = m_out_circular = 0, full
  m_in_virgin/m_out_linear, virgin GHG (FeSO₄ 0.000334, H₃PO₄ 1.066) in **both** linear &
  circular — because per Aparicio Eq. 7 the *circular system* still makes Fe/P virgin
  (they're not recoverable). Circular 519.19 → **584.5**, linear 2696.93 → **2762.24**.
  Note: the lower ECPI is driven mostly by **α** (Fe/P add to m_out_linear with
  m_out_circular = 0 → α_out 0.90 → 0.59, α_in 0.31 → 0.20).

**β is on a different principle in CI vs ECPI** (confirmed against the papers):
CI β = 1 − recycling-energy / primary-energy (Cullen, energy, cell-level); ECPI β =
1 − circular-system LCA / linear-system LCA (Aparicio, emissions, whole-system). That's
why Fe/P need no virgin-in-circular term in CI but do in ECPI. CI is correct as-is.

**Updated base case (Hydrothermal, 90 % collection):**

| | Iter 3 (Fe/P recovered 0.90) | Iter 4 (Fe/P recovery 0) |
|---|---|---|
| PCI | 0.410 | **0.240** |
| CI | 0.573 | **0.373** |
| CEI | 0.451 | **0.419** |
| ECPI | 0.224 | **0.095** |
| M | 0.629 | **0.605** |
| R / E | 0.620 / 0.638 | 0.620 / 0.638 |

**Solid-State route (Fe/P recovery 0), regenerated 2026-06-19:** PCI 0.239 · CI **0.332**
· CEI 0.419 · ECPI 0.095 · M 0.605 · R 0.620 · E 0.639
(`cumulative_results_solidstate_lfp.csv`; route still affects only CI). Solid sheets
`CI_solid` (Fe₃O₄/DAP recovery 0) and `ECPI_solid` (circular 584.5) refreshed.

**Documentation workbook:** `indicator_input_values_lfp.xlsx` edited **surgically — only the
8 Fe/P recovery cells** (CEI K7/K9, PCI L10/L11, CI K9/K10, MRE R6/R7 → 0); `CI_solid` /
`ECPI_solid` regenerated. The hand-curated **`ECPI_indicator`** sheet was **left untouched**
(its alpha-sum block is stale at 855.74; computation CSV is source of record at 584.5).

**Still open:** (1) refresh `ECPI_indicator` doc-sheet alpha-sum (855.74 → 584.5 + 2 Fe/P
rows) if wanted; (2) cathode-synthesis GHG (~367 kg) not added to ECPI (boundary choice);
(3) downstream **Cumulative table, S1/S2/S3, NMC-vs-LFP comparison** are stale vs Iter 4 —
re-run pending.

### Iteration 3 — 2026-06-18 (ECPI rebuild + cell-weight fix)

**ECPI restructured to the LiOH cell-mass-allocation method (matches the NMC811 worksheet logic):**
1. **m_out_circular = 0.9 × m_out_linear** → α_out = 0.90 (flat; was per-material collection×recovery, α_out 0.846).
2. **Lithium: recipe LiOH in, stoichiometric LiOH recovered.**
   - **m_in_virgin (LINEAR) = recipe LiOH = 44.894 kg** (= 0.26838 ton/ton × 167.28) — the LiOH
     actually consumed in cathode production (incl. process excess).
   - **Recovered (CIRCULAR) = stoichiometric in-cell LiOH = 25.394 kg** (= Li 7.36 ÷ 0.28984) —
     only the lithium physically in the cell is recoverable. The 44.894 excess is not in the cell.
3. **Li₂CO₃ ↔ LiOH:** 1 kg Li₂CO₃ = 0.6482 kg LiOH-equivalent (Li₂CO₃ + Ca(OH)₂ → 2 LiOH + CaCO₃).
   Recovered Li₂CO₃ expressed in LiOH-equivalent so input/output balance.
4. **CIRCULAR emissions — per-material recovery basis (matches the LFP input-values sheet):**
   - Cell recycling GHG = 0.78904 kg CO₂e/kg cell × **402.95 kg cell** = **317.94 kg CO₂e**,
     mass-allocated over in-cell recovered materials (LiOH-stoich 25.394 + Cu 61.358 + cell-Al
     19.763 = 106.52 kg) → **uniform 2.985 kg CO₂e/kg**.
   - LiOH (stoich 25.394) × 2.985 = 75.80; Cu 61.358 × 2.985 = 183.15; cell-Al 19.763 × 2.985 = 58.99.
   - **module+pack Al (56.085 kg) × 2.3548** (secondary recycled Al) = 132.08.
   - **steel recovered (0.9 × 118.59 = 106.73) × 0.648** (secondary steel) = 69.18.
   - **LCA_emissions_circular = 519.19** (= 75.80+183.15+58.99+132.08+69.18).
5. **LINEAR emissions = Σ(m_in_virgin × virgin GHG):** LiOH 44.894×22.677 + Cu 61.358×3.86 +
   Al 75.849×14.37 + steel 118.59×2.969 = **2696.93**. (β = 1 − 519.19/2696.93 = **0.8075**.)
   m_out_circular = 0.9 × m_out_linear → α_out = 0.90; α_in = 0.3089; **ECPI = 0.2245**.

**Cell weight corrected (carry-over fix):**
6. Cell weight = **402.95 kg** = sum of LFP cell components (active 167.28 + graphite 85.97 + binder 5.21
   + copper 61.36 + cell-Al 19.76 + LiPF₆ 7.70 + EC 21.34 + DMC 21.34 + PP 0.49 + PE 6.37 + polymer 5.03
   + PET 1.09). **Was** the NMC811 cell/pack ratio 0.62275 × 606.3 = 377.57 (a carry-over).
   Cell-Al = total Al 75.85 × OWinjobi LFP cell share (18.5/71 = 0.2606) = 19.76.
   → **CI dropped 0.605 → 0.573** (larger cell mass lowers cell α = recovered/cell_mass).
7. **Iron CEI virgin price = $1/kg** (was $0.50).

**Result (base case) — ECPI circular now reproduces the LFP input-values sheet exactly
(LCA_circular = 519.19, LCA_linear = 2696.93):** PCI 0.410 · **CI 0.573** · CEI 0.451 ·
**ECPI 0.2245** · M 0.629 · R 0.620 · E 0.638.

**ECPI circular resolution (all confirmed):**
- circular emissions use **full / recovered mass per material** (not a single 0.9 factor): cell
  materials at full in-cell mass × 2.985; steel at 0.9 × mass × 0.648; pack-Al at 56.085 × 2.3548.
- **Aluminium split:** cell-Al (19.76) at the cell rate 2.985; module+pack Al (56.085) at recycled-Al 2.3548.
- **Steel** recycled rate 0.648 (per-material secondary steel); **pack-Al** 2.3548 (secondary Al).

### Iteration 2 — 2026-06-17 (review corrections)
1. **Full GREET energy/GHG alignment** — removed all NMC811 energy carry-over. New
   `lfp_greet_data.py` is the single source of truth (every constant provenance-tagged).
   Per-material intensities from GREET §4.3 Li-Ion; LFP active material cradle-to-gate
   from the cathode recipe × precursor intensities + synthesis (108.7 mmBtu/ton). MRE
   E-block (`E_processing`, `E_total_2`, `QP_ipf`, `E_assembly`, `E_recovery`,
   `E_pre_treatment`) now recomputed from GREET (68 868 MJ total production).
2. **CI restructured to the NMC811 cell/pack split** —
   - Cell-level = cathode precursors **+ cell Al + cell Cu**; **graphite removed**;
     **NMP removed** (solvent, not a recovered cell material).
   - Pack-level = steel + aluminium (recyclable module+pack).
   - Hydro precursors: LiOH, H₃PO₄, FeSO₄ (FeSO₄ = 0 in GREET → 0.5 kWh/kg floor for
     the energy ratio only). Solid: Li₂CO₃, Fe₃O₄, DAP.
   - `cell_total` ADP-fossil is now a **dynamic sum of the LFP cell-material ADP**
     = **1609.95 MJ/kg** (was the NMC811-specific 6197.66 = Σ of the six NMC cell-material
     ADP values — LiOH 685.74 + Al 358.69 + Cu 944.78 + CoSO₄ 3182.67 + NiSO₄ 932.56 + MnSO₄ 93.23).
3. **Cell recycling energy = 6.35 mmBtu/ton** (LFP hydrometallurgical, GREET Battery
   Recycling → LFP → *Mass allocation*) = **2.044 kWh/kg** (NMC811 was 27.5 / 8.85225).
4. **Recycling process confirmed = hydrometallurgical** (same as NMC811; visible in the
   NMC ECPI sheet "Recycling → Hydrometallurgical processing").
5. **Iron CEI virgin price = $1/kg** (was $0.50).
6. **ECPI restructured** —
   - Materials = **LiOH, copper, aluminium, steel** (graphite **and** whole-LiFePO₄ removed,
     because the cathode is not recovered in entirety — only lithium).
   - Lithium tracked on **LiOH-equivalent** basis; recovered **Li₂CO₃ × 0.648 = LiOH** displaced
     (Li₂CO₃ + Ca(OH)₂ → 2 LiOH + CaCO₃). Mass-circularity α is consistent; the difference
     enters β (emissions).
   - Virgin GHG (kg CO₂e/kg): LiOH 22.68, Cu 3.86, Al 14.37, steel 2.97.
   - Recycled GHG: LiOH = **4.39** (= GREET Battery Recycling §2 Li₂CO₃ hydromet 2.846 t CO₂e/ton,
     mass allocation, ÷0.648), steel 0.648, Al 2.355, Cu 0.50.
   - Result: linear 2696.9, circular 855.7, **β 0.683, ECPI 0.178** (was 0.081).
7. **GREET LFP recycling mass-allocation factors recorded** (`LFP_RECYCLING_ALLOCATION`):
   Li₂CO₃ 13.4 % hydro, graphite 28.4 % hydro + 28.9 % direct, Cu 100 % pyro,
   LFP-cathode 58.6 % direct.
8. **File naming** — all deliverables suffixed `_lfp`; build scripts emit `_lfp` names.
9. **`indicator_input_values_lfp.xlsx`** reformatted to the **NMC811 layout** (BOM lb/kg
   left, M-block + LiFePO₄ decomposition, parameter table **+ Reference column**, References
   block). The user-curated **`ECPI_indicator`** sheet (GREET precursor LCA table, recycling
   data, allocation factors, GWP) is **preserved**; only the alpha-sum parameter block is
   refreshed in place.

### Open / flagged
- **Mass allocation** is the chosen GREET basis (economic allocation §1.6.2 also exists).
  The allocation factors (Li₂CO₃ 13.4 % hydro etc.) split **recycling emissions** among
  co-products — they are **NOT recovery rates**. Lithium recovery stays **0.90** (separate
  GREET/FHanna quantity).
- **Recycled GHG sourcing:** lithium = GREET Battery Recycling §2 (mass alloc, Li₂CO₃ 2.846
  → 4.39 LiOH-eq). Cu/Al/steel recycled GHG (0.50/2.355/0.648) are **literature** secondary-
  metal intensities — GREET §2 tabulates only the cathode-derived recovered materials
  (CoSO₄/NiSO₄/Li₂CO₃/MnSO₄), not Cu/Al/steel.
- **CI ADP-fossil** values are GREET-derived (precursor energy); can be switched to the GREET
  "Fossil fuels" row specifically if exact match to the NMC811 basis is wanted.
- **🔴 carried-over MRE methodology assumptions** (§8) — second-life pathways, qualitative
  scores, regional masses, sub-index weights (not chemistry-specific).

### Iteration 1 — 2026-06-15 (initial LFP build)
- Built the LFP pipeline mirroring NMC811: BOM from GREET, all five indicators + M/R/E,
  collection sweep, solid-state route, three-way comparison, sensitivity studies,
  documentation workbooks.
