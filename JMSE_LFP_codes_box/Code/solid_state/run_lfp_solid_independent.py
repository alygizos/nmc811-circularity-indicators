"""
run_lfp_solid_independent.py  —  LFP_codes_box edition
======================================================
One-command Solid-State pipeline for the shareable box.

Unlike the dev-repo version (which rebuilds the *_solid inputs from GREET via
build_lfp_inputs.py / build_lfp_mre.py), this box edition uses the `*_solid` input
CSVs **already included in the box** — so it needs no GREET data, no NMC reference
build, and no flat dev layout. It:
  1. runs the 5 indicators with LFP_ROUTE=solid  (they read *_solid.csv and write
     cumulative_results_indicators_solid.csv + *_solid.png),
  2. writes the 3-way comparison figure NMC811_vs_LFP_comparison_independent_lfp.png,
  3. prints the NMC811 vs LFP-Hydro vs LFP-Solid summary.

The hydro canon is never touched — the indicators route-separate their I/O by
LFP_ROUTE (hydro -> canonical names, solid -> *_solid). Run from Code/solid_state/.

  python run_lfp_solid_independent.py
"""
import os, sys, subprocess, csv
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))        # .../Code/solid_state
CODE = os.path.abspath(os.path.join(HERE, '..'))          # .../Code
PY   = sys.executable
ENV  = dict(os.environ, MPLBACKEND='Agg', PYTHONIOENCODING='utf-8', LFP_ROUTE='solid')

IND = [('PCI', 'pci_indicator_v2.py'), ('CI', 'ci_indicator.py'), ('CEI', 'cei_indicator.py'),
       ('ECPI', 'ecpi_indicator.py'), ('MRE', 'mre_indicator.py')]

def _dir(name):                       # tolerate CEI/cei case differences across OSes
    for c in (name, name.lower()):
        d = os.path.join(CODE, c)
        if os.path.isdir(d):
            return d
    raise FileNotFoundError(f"indicator dir not found: {name}")

CUM_SOLID = os.path.join(CODE, 'cumulative_results_indicators_solid.csv')
CUM_HYDRO = os.path.join(CODE, 'cumulative_results_indicators.csv')           # hydro canon (read-only)
CUM_NMC   = os.path.join(HERE, 'cumulative_results_indicators_nmc811.csv')    # bundled NMC811 reference

def run(script, cwd):
    r = subprocess.run([PY, '-X', 'utf8', script], cwd=cwd, env=ENV, capture_output=True, text=True)
    if r.returncode:
        print('ERROR', script, 'in', cwd); print(r.stderr[-1200:]); raise SystemExit(1)

def read_cum(path):
    out = {}
    if os.path.exists(path):
        with open(path) as f:
            for row in csv.DictReader(f):
                out[row['Indicator']] = (float(row['Mean']), float(row['CI_Lower']), float(row['CI_Upper']))
    return out

print("Running 5 indicators in SOLID mode (reading included *_solid CSVs; hydro canon untouched)...")
for name, script in IND:
    print(f"  {name} [solid] ...")
    run(script, _dir(name))

nmc, hydro, solid = read_cum(CUM_NMC), read_cum(CUM_HYDRO), read_cum(CUM_SOLID)
inds = ['PCI', 'CI', 'CEI', 'ECPI', 'M', 'R', 'E']
series = [('NMC811', nmc, '#7f8c8d'), ('LFP (Hydrothermal)', hydro, '#2980b9'),
          ('LFP (Solid-State)', solid, '#27ae60')]
x = np.arange(len(inds)); w = 0.26
fig, ax = plt.subplots(figsize=(13, 6.5))
for i, (label, data, color) in enumerate(series):
    means = [data.get(k, (0, 0, 0))[0] for k in inds]
    lo = [data.get(k, (0, 0, 0))[0] - data.get(k, (0, 0, 0))[1] for k in inds]
    hi = [data.get(k, (0, 0, 0))[2] - data.get(k, (0, 0, 0))[0] for k in inds]
    bars = ax.bar(x + (i - 1) * w, means, w, label=label, color=color,
                  edgecolor='black', linewidth=0.8, alpha=0.9)
    ax.errorbar(x + (i - 1) * w, means, yerr=[lo, hi], fmt='none',
                ecolor='black', elinewidth=1.3, capsize=4, capthick=1.3, zorder=10)
    for b, m in zip(bars, means):
        ax.text(b.get_x() + b.get_width() / 2, m + 0.008, f'{m:.3f}',
                ha='center', va='bottom', fontsize=7.5, rotation=90)
ax.set_xticks(x); ax.set_xticklabels(inds, fontsize=13, fontweight='bold')
ax.set_ylabel('Indicator value', fontsize=13, fontweight='bold')
ax.set_title('Circularity Indicators: NMC811 vs LFP routes (90% collection, 95% CI)',
             fontsize=14, fontweight='bold', pad=14)
ax.legend(fontsize=11, frameon=True); ax.grid(axis='y', alpha=0.3, ls='--'); ax.set_axisbelow(True)
plt.tight_layout()
out = os.path.join(HERE, 'NMC811_vs_LFP_comparison_independent_lfp.png')
plt.savefig(out, dpi=300, bbox_inches='tight'); print("Wrote", os.path.basename(out))

print(f"\n{'Indicator':>6} | {'NMC811':>8} | {'LFP-Hydro':>9} | {'LFP-Solid':>9}")
print('-' * 44)
for k in inds:
    print(f"{k:>6} | {nmc.get(k,(float('nan'),))[0]:>8.4f} | "
          f"{hydro.get(k,(float('nan'),))[0]:>9.4f} | {solid.get(k,(float('nan'),))[0]:>9.4f}")
print("\nSolid-state results -> cumulative_results_indicators_solid.csv (hydro canon untouched).")
