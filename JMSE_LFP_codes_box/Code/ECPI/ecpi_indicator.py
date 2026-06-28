"""
ECPI indicator (LFP) - revamped 2026-06-21
==========================================
The GHG (circular/linear) and alpha/beta math now lives HERE; the CSV holds only
RAW INPUTS (masses, virgin GHG, F_r, recycled GHG/kg rates, collection).

Methodology (ECPI = alpha * beta, Carmona Aparicio et al. 2025, Eq. 1-7):

  beta  (QUALITY / intensity) -- a PURE per-kg intensity ratio over the RECOVERABLE
        materials {Li-carrier, Cu, Al, steel}, SAME recoverable mass on both sides:
            beta = 1 - sum(M_recover * recycled_ghg) / sum(M_recover * virgin_ghg)
        Collection C and recovery F_r do NOT enter beta (that would double-count the
        quantity that alpha already measures). The cell recycling GHG (per kg cell) is
        allocated across the recoverable cell materials weighted by (M_recover * F_r)
        [NMC811-style]; the allocation PRESERVES the total cell GHG, so F_r reallocates
        the burden between materials but does not shrink the beta numerator.
        Fe/P (F_r = 0) have no recycled route -> excluded from beta.

  alpha (QUANTITY) -- carries collection and recovery:
            alpha_in  = sum(M_prod * in_circ) / sum(M_prod)          (recycled content)
            alpha_out = sum(M_prod * C * F_r) / sum(M_prod)          (collected & recovered)
            alpha     = alpha_in * alpha_out
        Fe/P (F_r = 0) stay in the totals and dilute alpha (recovered = 0).

CSV schema (see build_lfp_inputs.py):
  material, mass_recover, mass_prod, virgin_ghg, F_r, in_circ, cell_frac, recycled_ghg_direct
  PARAM_collection / PARAM_cell_recycling_ghg_per_kg / PARAM_cell_mass_kg  (value in mass_recover col)
"""
import csv
import os
import copy
import numpy as np
import matplotlib
matplotlib.use('Agg')          # headless-safe; no blocking plt.show()
import matplotlib.pyplot as plt
import seaborn as sns


# --------------------------------------------------------------------------- IO
def load_ecpi_inputs(csv_path='ECPI_indicator_alpha_sum.csv'):
    """Parse the raw-input CSV into (materials list, params dict)."""
    mats, params = [], {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            name = row['material']
            if name.startswith('PARAM_'):
                params[name[len('PARAM_'):]] = float(row['mass_recover'])
                continue

            def num(key):
                v = row.get(key, '')
                return float(v) if v not in (None, '') else 0.0

            mats.append({
                'name'      : name,
                'mass_recover': num('mass_recover'),
                'mass_prod'   : num('mass_prod'),
                'virgin_ghg'  : num('virgin_ghg'),
                'F_r'         : num('F_r'),
                'in_circ'     : num('in_circ'),
                'cell_frac'   : num('cell_frac'),
                'rec_direct'  : num('recycled_ghg_direct'),
                'fr_on_direct': num('fr_on_direct'),
            })
    return mats, params


# -------------------------------------------------------------------- core math
def compute_ecpi(mats, params, mode='eq2'):
    """
    Compute alpha/beta/ECPI plus the GHG breakdown from raw inputs.

    mode='eq2' (default, USER 2026-06-21 — Cullen Eq.2, recover-vs-primary):
        Over the RECOVERED materials only {LiOH, Cu, Al, steel}; Fe/P are excluded from
        BOTH sides (not recovered -> not part of the recover-vs-primary comparison).
            circular = recycling-credit GHG (sum of rec_ghg_abs)            = 513.78
            linear   = primary (virgin) production at the PRODUCTION mass    = 2696.94
                       (mass_prod * virgin_ghg; LiOH uses the recipe 44.894, not stoich)
            beta = 1 - 513.78/2696.94 = 0.8095 (hydro)
        Fe/P virgin is NOT in circular (no virgin in the numerator) and NOT in linear.
    mode='whole_system' (Eq. 7, NOT used — kept for reference):
        circular also adds the virgin production of everything NOT recovered (Fe/P +
        recipe-excess Li) and linear is the full battery -> circular 1021.3, beta 0.630.
    mode='intensity':
        like eq2 but linear uses the RECOVER (stoich) mass for lithium -> 2254.7, beta 0.772.

    Cell recycling GHG (per kg cell) is allocated over the recoverable cell materials
    weighted by (mass_recover * F_r); the allocation PRESERVES the cell total.
    fr_on_direct=1 multiplies F_r into a material's direct (secondary) recycled rate.

    Annotates each material with 'rec_ghg_abs' / 'rec_ghg_per_kg' for reporting.
    """
    C         = params['collection']
    cell_rate = params['cell_recycling_ghg_per_kg']   # kg CO2e / kg cell
    cell_mass = params['cell_mass_kg']

    # --- cell recycling GHG, F_r-weighted allocation over recoverable cell materials ---
    total_cell_ghg = cell_mass * cell_rate
    cell_weight = sum(m['mass_recover'] * m['cell_frac'] * m['F_r'] for m in mats)
    per_weight  = total_cell_ghg / cell_weight if cell_weight else 0.0

    circular = 0.0
    linear   = 0.0
    for m in mats:
        cell_part   = m['mass_recover'] * m['cell_frac'] * m['F_r'] * per_weight
        fr_dir      = m['F_r'] if m['fr_on_direct'] else 1.0          # F_r into steel rate
        direct_part = m['mass_recover'] * (1.0 - m['cell_frac']) * fr_dir * m['rec_direct']
        m['rec_ghg_abs']    = cell_part + direct_part                 # recycled-credit GHG
        m['rec_ghg_per_kg'] = (m['rec_ghg_abs'] / m['mass_recover']) if m['mass_recover'] else 0.0

        recovered_mass = m['mass_recover'] if m['F_r'] > 0 else 0.0   # in-cell amount recycled
        if mode == 'eq2':
            # Cullen Eq.2: recovered materials ONLY (Fe/P excluded from both sides).
            # numerator = recycled-credit GHG; denominator = primary production GHG at the
            # PRODUCTION (recipe) mass -> linear uses mass_prod (LiOH 44.894, not stoich).
            if m['F_r'] > 0:
                circular += m['rec_ghg_abs']
                linear   += m['mass_prod'] * m['virgin_ghg']
        elif mode == 'whole_system':
            # Eq.7: recycled credit + virgin for the produced-but-not-recovered remainder
            virgin_part = (m['mass_prod'] - recovered_mass) * m['virgin_ghg']
            circular += m['rec_ghg_abs'] + virgin_part
            linear   += m['mass_prod'] * m['virgin_ghg']
        else:  # intensity: recoverable only, same RECOVER (stoich) mass on both sides
            if m['F_r'] > 0:
                circular += m['rec_ghg_abs']
                linear   += m['mass_recover'] * m['virgin_ghg']

    beta = 1.0 - circular / linear

    # --- alpha (quantity): collection + recovery live here ---
    tot_prod  = sum(m['mass_prod'] for m in mats)
    alpha_in  = sum(m['mass_prod'] * m['in_circ']    for m in mats) / tot_prod
    alpha_out = sum(m['mass_prod'] * C * m['F_r']    for m in mats) / tot_prod
    alpha     = alpha_in * alpha_out

    ecpi = alpha * beta
    return {
        'ecpi': ecpi, 'alpha': alpha, 'alpha_in': alpha_in, 'alpha_out': alpha_out,
        'beta': beta, 'circular': circular, 'linear': linear,
        'cell_ghg_total': total_cell_ghg, 'collection': C, 'mode': mode,
    }


# ------------------------------------------------------------------- reporting
def print_ecpi_results(mats, res):
    print("\n" + "=" * 84)
    print("ECPI (Environmental Circular Performance Index) RESULTS  [revamp 2026-06-21]")
    print("=" * 84)
    print(f"\nCollection C = {res['collection']:.2f}   "
          f"cell recycling GHG total = {res['cell_ghg_total']:.2f} kg CO2e (F_r-allocated)")
    print("-" * 84)
    print(f"{'material':<12}{'M_recover':>11}{'M_prod':>10}{'F_r':>7}"
          f"{'recyc GHG/kg':>14}{'virgin GHG/kg':>15}")
    print("-" * 84)
    ws = res['mode'] == 'whole_system'
    notrec = '  (not recovered -> virgin in BOTH)' if ws else '  (not recoverable -> alpha only)'
    for m in mats:
        tag = '' if m['F_r'] > 0 else notrec
        print(f"{m['name']:<12}{m['mass_recover']:>11.3f}{m['mass_prod']:>10.3f}"
              f"{m['F_r']:>7.2f}{m['rec_ghg_per_kg']:>14.4f}{m['virgin_ghg']:>15.4f}{tag}")
    print("-" * 84)
    scope = 'whole-system' if ws else 'recoverable'
    print(f"  circular ({scope}):  {res['circular']:.4f} kg CO2-eq")
    print(f"  linear   ({scope}):  {res['linear']:.4f} kg CO2-eq")
    print("-" * 84)
    print(f"  alpha_in  (recycled content): {res['alpha_in']:.4f}")
    print(f"  alpha_out (collected*F_r):    {res['alpha_out']:.4f}")
    print(f"  alpha (product):              {res['alpha']:.4f}")
    print(f"  beta  (1 - circ/lin):         {res['beta']:.4f}")
    print("-" * 84)
    print(f"  ECPI: {res['ecpi']:.4f}   ({res['ecpi']*100:.2f}%)")
    print("=" * 84 + "\n")


# ------------------------------------------------------------- uncertainty (MC)
def _perturb(mats, params, unc, rng):
    """Return perturbed (mats, params): jitter recoverable masses + recycled rates."""
    m2 = copy.deepcopy(mats)
    p2 = dict(params)
    for m in m2:
        if m['mass_recover'] > 0:
            m['mass_recover'] = max(0.0, rng.normal(m['mass_recover'], m['mass_recover'] * unc))
        if m['rec_direct'] > 0:
            m['rec_direct'] = max(0.0, rng.normal(m['rec_direct'], m['rec_direct'] * unc))
    p2['cell_recycling_ghg_per_kg'] = max(
        0.0, rng.normal(params['cell_recycling_ghg_per_kg'],
                        params['cell_recycling_ghg_per_kg'] * unc))
    return m2, p2


def monte_carlo_ecpi(csv_path='ECPI_indicator_alpha_sum.csv', n_samples=1000,
                     uncertainty_pct=0.05, confidence_level=0.95):
    mats, params = load_ecpi_inputs(csv_path)
    rng = np.random.default_rng()
    vals = []
    for _ in range(n_samples):
        m2, p2 = _perturb(mats, params, uncertainty_pct, rng)
        vals.append(compute_ecpi(m2, p2)['ecpi'])
    vals = np.array(vals)
    a = 1 - confidence_level
    mean_val, std_val = float(np.mean(vals)), float(np.std(vals))
    lo = float(np.percentile(vals, a / 2 * 100))
    hi = float(np.percentile(vals, (1 - a / 2) * 100))
    stats = {'mean': mean_val, 'std': std_val, 'lower_ci': lo, 'upper_ci': hi,
             'error_bar': (mean_val - lo, hi - mean_val)}
    return stats, vals


# ------------------------------------------------------------------- plotting
def plot_ecpi_bar_chart(ecpi_value, save_path='ecpi_bar_chart.png', dpi=300, figsize=(6, 6)):
    sns.set_style("whitegrid"); sns.set_context("paper", font_scale=1.5)
    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.bar([0], [ecpi_value], color=['#9b59b6'], edgecolor='black',
                  linewidth=1.2, alpha=0.8, width=0.5)
    ax.set_ylabel('ECPI Value', fontweight='bold', fontsize=14)
    ax.set_title('Environmental Circular Performance Index\n(Carmona Aparicio et al., 2025)',
                 fontweight='bold', fontsize=14, pad=20)
    ax.set_xticks([0]); ax.set_xticklabels(['Cumulative ECPI'])
    ax.text(0, bars[0].get_height(), f'{ecpi_value:.4f}\n({ecpi_value*100:.2f}%)',
            ha='center', va='bottom', fontsize=12, fontweight='bold')
    ax.yaxis.grid(True, linestyle='--', alpha=0.7); ax.set_axisbelow(True)
    ax.set_ylim(0, max(1.0, ecpi_value * 1.15))
    plt.tight_layout(); plt.savefig(save_path, dpi=dpi, bbox_inches='tight'); plt.close(fig)
    print(f"ECPI bar chart saved to: {save_path}")


def plot_ecpi_with_error_bars(csv_path='ECPI_indicator_alpha_sum.csv', n_samples=1000,
                              uncertainty_pct=0.05, save_path='ecpi_with_error_bars.png',
                              dpi=300, figsize=(6, 6)):
    print(f"\nRunning Monte Carlo simulation with {n_samples} samples...")
    stats, _ = monte_carlo_ecpi(csv_path, n_samples, uncertainty_pct)
    sns.set_style("whitegrid"); sns.set_context("paper", font_scale=1.5)
    fig, ax = plt.subplots(figsize=figsize)
    mean = stats['mean']; el, eu = stats['error_bar']
    ax.bar([0], [mean], color=['#9b59b6'], edgecolor='black', linewidth=1.2, alpha=0.8, width=0.5)
    ax.errorbar([0], [mean], yerr=[[el], [eu]], fmt='none', ecolor='black',
                capsize=5, capthick=2, linewidth=2)
    ax.set_ylabel('ECPI Value', fontweight='bold', fontsize=14)
    ax.set_title(f'ECPI with 95% CI\n(Monte Carlo: {n_samples} samples, {uncertainty_pct*100}% unc.)',
                 fontweight='bold', fontsize=14, pad=20)
    ax.set_xticks([0]); ax.set_xticklabels(['Cumulative ECPI'])
    ax.text(0, mean, f'{mean:.4f}\n({mean*100:.2f}%)', ha='center', va='bottom',
            fontsize=11, fontweight='bold')
    ax.yaxis.grid(True, linestyle='--', alpha=0.7); ax.set_axisbelow(True)
    ax.set_ylim(0, max(1.0, mean * 1.2))
    plt.tight_layout(); plt.savefig(save_path, dpi=dpi, bbox_inches='tight'); plt.close(fig)
    print(f"ECPI bar chart with error bars saved to: {save_path}")
    print("\n" + "=" * 70)
    print("MONTE CARLO RESULTS")
    print("=" * 70)
    print(f"  Mean ECPI:   {stats['mean']:.6f}")
    print(f"  Std Dev:     {stats['std']:.6f}")
    print(f"  95% CI:      [{stats['lower_ci']:.6f}, {stats['upper_ci']:.6f}]")
    print("=" * 70)
    return stats


def tornado_plot_ecpi(csv_path='ECPI_indicator_alpha_sum.csv', variation_pct=0.05,
                      save_path='ecpi_tornado.png', dpi=300, figsize=(10, 6)):
    """Sensitivity of ECPI to the key recycled-GHG rates, collection, and recovery."""
    mats, params = load_ecpi_inputs(csv_path)
    base = compute_ecpi(copy.deepcopy(mats), dict(params))['ecpi']

    def with_param(key, factor):
        p = dict(params); p[key] = params[key] * factor
        return compute_ecpi(copy.deepcopy(mats), p)['ecpi']

    def with_recovery(factor):
        m2 = copy.deepcopy(mats)
        for m in m2:
            if m['F_r'] > 0:
                m['F_r'] = min(1.0, m['F_r'] * factor)
        return compute_ecpi(m2, dict(params))['ecpi']

    def with_rate(field, factor):  # scale every material's recycled_ghg_direct
        m2 = copy.deepcopy(mats)
        for m in m2:
            m[field] = m[field] * factor
        return compute_ecpi(m2, dict(params))['ecpi']

    levers = {
        'cell_recycling_ghg': (with_param('cell_recycling_ghg_per_kg', 1 - variation_pct),
                               with_param('cell_recycling_ghg_per_kg', 1 + variation_pct)),
        'collection':         (with_param('collection', 1 - variation_pct),
                               with_param('collection', 1 + variation_pct)),
        'recovery_F_r':       (with_recovery(1 - variation_pct), with_recovery(1 + variation_pct)),
        'secondary_rates':    (with_rate('rec_direct', 1 - variation_pct),
                               with_rate('rec_direct', 1 + variation_pct)),
    }
    impacts = {k: {'low': lo - base, 'high': hi - base, 'range': abs(hi - lo)}
               for k, (lo, hi) in levers.items()}
    order = sorted(impacts.items(), key=lambda x: x[1]['range'], reverse=True)

    sns.set_style("whitegrid"); sns.set_context("paper", font_scale=1.3)
    fig, ax = plt.subplots(figsize=figsize)
    y = np.arange(len(order))
    ax.barh(y, [p[1]['low']  for p in order], height=0.4, color='#d73027', alpha=0.8,
            label=f'-{variation_pct*100:.0f}%')
    ax.barh(y, [p[1]['high'] for p in order], height=0.4, color='#4575b4', alpha=0.8,
            label=f'+{variation_pct*100:.0f}%')
    ax.axvline(x=0, color='black', linewidth=2)
    ax.set_yticks(y); ax.set_yticklabels([p[0].replace('_', ' ').title() for p in order])
    ax.set_xlabel('Change in ECPI', fontweight='bold', fontsize=14)
    ax.set_title(f'Tornado: ECPI sensitivity (base {base:.4f}, +/-{variation_pct*100:.0f}%)',
                 fontweight='bold', fontsize=14, pad=20)
    ax.xaxis.grid(True, linestyle='--', alpha=0.7); ax.set_axisbelow(True)
    ax.legend(loc='best', frameon=True)
    plt.tight_layout(); plt.savefig(save_path, dpi=dpi, bbox_inches='tight'); plt.close(fig)
    print(f"Tornado plot saved to: {save_path}")
    print("\n" + "=" * 70)
    print("TORNADO - ECPI sensitivity")
    print("=" * 70)
    print(f"Base ECPI: {base:.6f}")
    for k, d in order:
        print(f"  {k:<22} low {d['low']:+.6f}  high {d['high']:+.6f}  range {d['range']:.6f}")
    print("=" * 70)
    return impacts


# ------------------------------------------------------------------------ main
if __name__ == "__main__":
    SUF = '_solid' if os.environ.get('LFP_ROUTE') == 'solid' else ''
    csv_file = f'ECPI_indicator_alpha_sum{SUF}.csv'

    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found! Run build_lfp_inputs.py first.")
    else:
        mats, params = load_ecpi_inputs(csv_file)
        res = compute_ecpi(mats, params)
        print_ecpi_results(mats, res)

        plot_ecpi_bar_chart(res['ecpi'], save_path=f'ecpi_bar_chart{SUF}.png')
        stats = plot_ecpi_with_error_bars(csv_path=csv_file, n_samples=1000,
                                          uncertainty_pct=0.05,
                                          save_path=f'ecpi_with_error_bars{SUF}.png')

        # --- write ECPI row into the cumulative indicator table ---
        cumulative_csv_path = os.path.join('..', f'cumulative_results_indicators{SUF}.csv')
        existing = {}
        if os.path.exists(cumulative_csv_path):
            with open(cumulative_csv_path, 'r') as f:
                for row in csv.DictReader(f):
                    existing[row['Indicator']] = row
        existing['ECPI'] = {'Indicator': 'ECPI', 'Mean': f"{stats['mean']:.6f}",
                            'CI_Lower': f"{stats['lower_ci']:.6f}",
                            'CI_Upper': f"{stats['upper_ci']:.6f}"}
        with open(cumulative_csv_path, 'w', newline='') as f:
            wtr = csv.DictWriter(f, fieldnames=['Indicator', 'Mean', 'CI_Lower', 'CI_Upper'])
            wtr.writeheader()
            for ind in ['PCI', 'CI', 'CEI', 'ECPI']:
                if ind in existing:
                    wtr.writerow(existing[ind])
        print(f"\nECPI results saved to {cumulative_csv_path}")

        tornado_plot_ecpi(csv_path=csv_file, variation_pct=0.05, save_path=f'ecpi_tornado{SUF}.png')
        print("\nAll tasks completed.")
