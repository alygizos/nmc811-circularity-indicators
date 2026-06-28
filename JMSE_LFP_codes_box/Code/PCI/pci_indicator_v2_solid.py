from typing import Sequence
import math
import csv
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from SALib.sample import saltelli
from SALib.analyze import sobol
import pandas as pd
from matplotlib.patches import Patch
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset
from matplotlib.transforms import Bbox, TransformedBbox
from mpl_toolkits.axes_grid1.inset_locator import BboxConnector, BboxPatch

# Parameter name mapping for plots (short code to full descriptive name)
PARAM_FULL_NAMES = {
    'F_u': 'Fraction of reused component',
    'F_r': 'Fraction of recycled content',
    'C_u': 'Collected fraction for reuse',
    'C_r': 'Collected ratio for recycling',
    'E_cp': 'Efficiency of component production',
    'E_fp': 'Efficiency of feedstock production',
    'C_fp': 'Frac. material losses recovered\n(feedstock production)',
    'C_cp': 'Frac. material losses recovered\n(component production)',
    'E_ms': 'Efficiency of material separation',
    'E_rfp': 'Efficiency of recycling process',
    'X': 'Utility factor'
}


def load_material_parameters(csv_file='pci_material_parameters_solid.csv'):
    """
    Load material parameters from CSV file.

    Args:
        csv_file: Path to the CSV file containing material parameters

    Returns:
        Tuple of (materials_dict, total_battery_mass) where materials_dict contains
        material parameters and total_battery_mass is the total battery weight in kg
    """
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, csv_file)

    materials = {}
    total_battery_mass = None

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            material_name = row['material']

            # Check if this is the total battery mass configuration row
            if material_name == 'TOTAL_BATTERY_MASS':
                total_battery_mass = float(row['M'])
                continue  # Skip this row for material parameters

            # Convert all numeric values to float
            params = {
                'M': float(row['M']),
                'F_u': float(row['F_u']),
                'F_r': float(row['F_r']),
                'C_u': float(row['C_u']),
                'C_r': float(row['C_r']),
                'E_cp': float(row['E_cp']),
                'E_fp': float(row['E_fp']),
                'C_fp': float(row['C_fp']),
                'C_cp': float(row['C_cp']),
                'E_ms': float(row['E_ms']),
                'E_rfp': float(row['E_rfp']),
                'X': float(row['X'])
            }
            materials[material_name] = params

    if total_battery_mass is None:
        raise ValueError("TOTAL_BATTERY_MASS not found in CSV file. Please add it as the first data row.")

    return materials, total_battery_mass


def compute_pci_for_material(params):
    """
    Generic function to compute PCI for any material given its parameters.

    Args:
        params: Dictionary containing all material parameters (M, F_u, F_r, etc.)

    Returns:
        PCI value for the material
    """
    # Extract parameters
    M = params['M']
    F_u = params['F_u']
    F_r = params['F_r']
    C_u = params['C_u']
    C_r = params['C_r']
    E_cp = params['E_cp']
    E_fp = params['E_fp']
    C_fp = params['C_fp']
    C_cp = params['C_cp']
    E_ms = params['E_ms']
    E_rfp = params['E_rfp']
    X = params['X']

    # ============== CALCULATIONS ===================

    V     = ((1 - F_u) * M * (1 - F_r)) / (E_cp * E_fp)
    W_fp  = (((1 - F_u) * M) / (E_fp * E_cp)) * (1 - E_fp) * (1 - C_fp)
    W_cp  = (((1 - F_u) * M) / E_cp) * E_fp * (1 - E_cp) * (1 - C_cp)
    W_u   = M * (1 - C_r - C_u)
    W_ms  = M * (1 - E_ms) * C_r
    W_rfp = M * E_ms * C_r * (1 - E_rfp)
    W     = W_fp + W_cp + W_u + W_ms + W_rfp

    R_in = F_r * (((1 - F_u) * M) / (E_fp * E_cp))
    R_out = (1 - E_fp) * C_fp * (((1 - F_u) * M) / (E_fp * E_cp)) + (1 - E_cp) * C_cp * (M / E_cp) + E_rfp * E_ms * C_r * M

    R = abs(R_in - R_out)
    C = abs(M * (F_u - C_u))

    V_linear = M / (E_cp * E_fp)
    W_linear = V_linear - M

    LFI = (V + W + 0.5 * R + 0.5 * C) / (V_linear + W_linear)
    PCI = 1.0 - (LFI / X)

    # Keep PCI within its meaningful range:
    # 0 = linear / no circularity benefit
    # 1 = fully circular
    # This prevents materials with no recovery, such as phosphorus and iron,
    # from producing mathematically negative PCI values.
    PCI = float(np.clip(PCI, 0.0, 1.0))

    return PCI


def compute_final_pci(csv_file='pci_material_parameters.csv'):
    """
    Compute final PCI value based on all materials.

    Args:
        csv_file: Path to the CSV file containing material parameters

    Returns:
        Tuple of (FINAL_PCI, pcis_dict) where pcis_dict contains individual material PCI values
    """
    # Load material parameters and total battery mass from CSV
    materials, Total_EVB_Mass = load_material_parameters(csv_file)

    # Compute PCI for each material
    pcis = {}
    masses = {}

    for material_name, params in materials.items():
        pcis[material_name] = compute_pci_for_material(params)
        masses[material_name] = params['M']

    # Calculate final weighted PCI
    FINAL_PCI = sum(pcis[k] * masses[k] for k in masses) / Total_EVB_Mass

    return FINAL_PCI, pcis


def print_pci_results(csv_file='pci_material_parameters.csv'):
    """
    Print PCI results for all materials and the final weighted PCI.

    Args:
        csv_file: Path to the CSV file containing material parameters
    """
    final_pci, material_pcis = compute_final_pci(csv_file)

    print("=" * 70)
    print("PCI INDICATOR RESULTS")
    print("=" * 70)
    print("\nIndividual Material PCI Values:")
    print("-" * 70)

    for material, pci in material_pcis.items():
        print(f"{material:<30} PCI: {pci:>10.4f}")

    print("-" * 70)
    print(f"\n{'FINAL WEIGHTED PCI':<30} {final_pci:>10.4f}")
    print("=" * 70)

    return final_pci, material_pcis


def plot_pci_bar_chart(csv_file='pci_material_parameters.csv', save_path='pci_bar_chart.png',
                       dpi=300, figsize=(10, 6)):
    """
    Create a journal-quality bar plot for PCI indicator.

    Args:
        csv_file: Path to the CSV file containing material parameters
        save_path: Path to save the figure
        dpi: Resolution for saved figure
        figsize: Figure size (width, height) in inches
    """
    final_pci, material_pcis = compute_final_pci(csv_file)

    # Set publication-quality style
    sns.set_style("whitegrid")
    sns.set_context("paper", font_scale=1.5)

    # Create figure and axis
    fig, ax = plt.subplots(figsize=figsize)

    # Prepare data
    materials = list(material_pcis.keys())
    pci_values = list(material_pcis.values())

    # Create color palette
    colors = sns.color_palette("viridis", len(materials))

    # Create bar plot
    bars = ax.bar(range(len(materials)), pci_values, color=colors,
                   edgecolor='black', linewidth=1.2, alpha=0.8)

    # Customize plot
    ax.set_xlabel('Material', fontweight='bold', fontsize=14)
    ax.set_ylabel('PCI Value', fontweight='bold', fontsize=14)
    ax.set_title('Process Circularity Indicator (PCI) by Material',
                 fontweight='bold', fontsize=16, pad=20)

    # Set x-axis labels
    ax.set_xticks(range(len(materials)))
    ax.set_xticklabels(materials, rotation=45, ha='right')

    # Add horizontal line for final weighted PCI
    ax.axhline(y=final_pci, color='red', linestyle='--', linewidth=2,
               label=f'Weighted Average: {final_pci:.4f}')

    # Add value labels on top of bars
    for i, (bar, val) in enumerate(zip(bars, pci_values)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.3f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Add grid for better readability
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    # Add legend
    ax.legend(loc='best', frameon=True, shadow=True)

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Save figure
    plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
    print(f"\nBar chart saved to: {save_path}")

    plt.show()

    return fig, ax


def monte_carlo_pci(csv_file='pci_material_parameters.csv', n_samples=10000,
                    uncertainty_pct=0.05, confidence_level=0.95):
    """
    Perform Monte Carlo simulation to estimate uncertainty in PCI values.

    Args:
        csv_file: Path to the CSV file containing material parameters
        n_samples: Number of Monte Carlo samples
        uncertainty_pct: Uncertainty as a fraction of the mean (e.g., 0.05 = 5%)
        confidence_level: Confidence level for error bars (e.g., 0.95 = 95%)

    Returns:
        Dictionary containing mean PCI, standard deviation, and confidence intervals
    """
    # Load base material parameters
    materials, Total_EVB_Mass = load_material_parameters(csv_file)

    # Storage for results
    mc_results = {material: [] for material in materials.keys()}
    mc_results['FINAL_PCI'] = []

    # Monte Carlo sampling
    for _ in range(n_samples):
        pcis = {}
        masses = {}

        for material_name, params in materials.items():
            # Create perturbed parameters (assuming normal distribution)
            perturbed_params = {}
            for key, value in params.items():
                # Add random noise to each parameter
                std_dev = abs(value * uncertainty_pct)
                perturbed_value = np.random.normal(value, std_dev)
                # Ensure non-negative values where appropriate
                if key in ['M', 'E_cp', 'E_fp', 'E_ms', 'E_rfp']:
                    perturbed_value = max(0.001, perturbed_value)
                # Ensure fractions stay between 0 and 1
                if key in ['F_u', 'F_r', 'C_u', 'C_r', 'C_fp', 'C_cp']:
                    perturbed_value = np.clip(perturbed_value, 0, 1)
                perturbed_params[key] = perturbed_value

            # Compute PCI with perturbed parameters
            pci = compute_pci_for_material(perturbed_params)
            pcis[material_name] = pci
            masses[material_name] = perturbed_params['M']
            mc_results[material_name].append(pci)

        # Calculate final weighted PCI
        final_pci = sum(pcis[k] * masses[k] for k in masses) / Total_EVB_Mass
        mc_results['FINAL_PCI'].append(final_pci)

    # Calculate statistics
    alpha = 1 - confidence_level
    stats = {}

    for key, values in mc_results.items():
        values_array = np.array(values)
        mean_val = np.mean(values_array)
        std_val = np.std(values_array)
        lower_ci = np.percentile(values_array, alpha/2 * 100)
        upper_ci = np.percentile(values_array, (1 - alpha/2) * 100)

        stats[key] = {
            'mean': mean_val,
            'std': std_val,
            'lower_ci': lower_ci,
            'upper_ci': upper_ci,
            'error_bar': (mean_val - lower_ci, upper_ci - mean_val)
        }

    return stats, mc_results


def plot_pci_with_error_bars(csv_file='pci_material_parameters.csv', n_samples=1000,
                             uncertainty_pct=0.05, save_path='pci_with_error_bars.png',
                             dpi=800, figsize=(10, 9)):
    """
    Create bar plot with Monte Carlo error bars.

    Args:
        csv_file: Path to the CSV file containing material parameters
        n_samples: Number of Monte Carlo samples
        uncertainty_pct: Uncertainty as a fraction of the mean
        save_path: Path to save the figure
        dpi: Resolution for saved figure
        figsize: Figure size
    """
    print(f"\nRunning Monte Carlo simulation with {n_samples} samples...")
    stats, mc_results = monte_carlo_pci(csv_file, n_samples, uncertainty_pct)

    # Include FINAL_PCI as a bar in the plot
    materials = [k for k in stats.keys() if k != 'FINAL_PCI']
    materials.append('FINAL_PCI')  # Add total to the end

    # Set publication-quality style
    sns.set_style("whitegrid")
    sns.set_context("paper", font_scale=1.5)

    # Create figure with adjusted size for extra bar
    fig, ax = plt.subplots(figsize=(figsize[0] + 1, figsize[1]))

    # Prepare data - include all materials plus FINAL_PCI
    means = [stats[m]['mean'] for m in materials]
    errors_lower = [stats[m]['error_bar'][0] for m in materials]
    errors_upper = [stats[m]['error_bar'][1] for m in materials]

    # Create color palette - different color for FINAL_PCI
    colors = [
    "#94D2BD",  # strong warm red
    "#94D2BD",  # mid warm coral
    "#94D2BD",  # soft salmon
    "#94D2BD",  # light warm-neutral
    "#94D2BD",  # light cool-neutral
    "#94D2BD",  # sky blue
    "#005F73",  # medium blue
    
    ]

    # Create bar plot with error bars
    x_pos = np.arange(len(materials), dtype=float)

    # Add extra spacing before FINAL_PCI
    gap = 1.3   # adjust for more/less space
    x_pos[-1] = x_pos[-2] + gap
    
    bars = ax.bar(
    x_pos,
    means,
    color=colors,
    edgecolor='black',
    linewidth=1.5,
    alpha=1,
    width=0.45
)
    
    # ---- NEW: vertical dashed line after lithium and before FINAL_PCI ----
    # Vertical dashed separator before Total PCI
    if len(materials) > 1:
        sep_x = (x_pos[-2] + x_pos[-1]) / 2

        ax.axvline(
            sep_x,
            color='black',
            linestyle=(0, (4, 4)),
            linewidth=1.5,
            alpha=0.4
        )
   
    ax.errorbar(x_pos, means, yerr=[errors_lower, errors_upper],
                fmt='none', ecolor='black', capsize=4, capthick=2, linewidth=2)

    for i, bar in enumerate(bars):
       height = bar.get_height()
       ax.text(
           bar.get_x() + bar.get_width() / 2,   # x position (center of bar)
           height + errors_upper[i] + 0.01,     # y position slightly above error bar
           f"{means[i]:.3f}",                   # formatted value (4 decimals)
           ha='center', va='bottom', fontsize=15, fontweight='bold'
           )

    # Customize plot
    #ax.set_xlabel('Material', fontsize=21)
    ax.set_ylabel('PCI', fontsize=15, fontweight='bold')
    #ax.set_title(f'PCI with 95% Confidence Intervals\n(Monte Carlo: {n_samples} samples, {uncertainty_pct*100}% uncertainty)',
     #            fontweight='bold', fontsize=11, pad=20)

    # Set x-axis labels - replace FINAL_PCI with "Total (Weighted)"
    label_names = [m if m != 'FINAL_PCI' else 'Total PCI' for m in materials]
    ax.set_xticks(x_pos)
    ax.set_xticklabels(label_names, ha='center', fontweight='bold', fontsize=15)

    ax.tick_params(axis='y', labelsize=15)

    # Add grid
    ax.grid(True, axis='y', color='#E0E0E0', linestyle='-', linewidth=0.5)
    ax.xaxis.grid(False)

    # Adjust layout
    plt.tight_layout()
    # Remove top and right border
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.0)
        spine.set_color("grey")
    # Save figure
    plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
    print(f"Bar chart with error bars saved to: {save_path}")

    plt.show()

    # Print statistics
    print("\n" + "=" * 70)
    print("MONTE CARLO SIMULATION RESULTS")
    print("=" * 70)
    for material in materials:
        if material == 'FINAL_PCI':
            print(f"\nFINAL WEIGHTED PCI:")
        else:
            print(f"\n{material}:")
        s = stats[material]
        print(f"  Mean PCI:    {s['mean']:.4f}")
        print(f"  Std Dev:     {s['std']:.4f}")
        print(f"  95% CI:      [{s['lower_ci']:.4f}, {s['upper_ci']:.4f}]")
    print("=" * 70)

    return fig, ax, stats


def sensitivity_analysis(csv_file='pci_material_parameters.csv', material_name=None,
                        n_samples=1024, save_path='pci_sensitivity.png'):
    """
    Perform global sensitivity analysis using Sobol indices.

    Args:
        csv_file: Path to the CSV file containing material parameters
        material_name: Specific material to analyze (if None, analyzes first material)
        n_samples: Number of samples for Sobol analysis (will be multiplied by (2*n_params + 2))
        save_path: Path to save sensitivity plot

    Returns:
        Dictionary containing Sobol indices
    """
    # Load material parameters
    materials, Total_EVB_Mass = load_material_parameters(csv_file)

    # Select material to analyze
    if material_name is None:
        material_name = list(materials.keys())[0]

    if material_name not in materials:
        raise ValueError(f"Material {material_name} not found in CSV")

    base_params = materials[material_name]

    # Define parameter names and bounds
    param_names = ['F_u', 'F_r', 'C_u', 'C_r', 'E_cp', 'E_fp', 'C_fp', 'C_cp', 'E_ms', 'E_rfp', 'X']

    # Define problem for SALib (±5% variation around base values)
    # Ensure bounds are valid (lower < upper)
    bounds = []
    for p in param_names:
        base_val = base_params[p]
        if base_val == 0 or abs(base_val) < 1e-10:
            # If base value is 0 or very small, use a small range
            bounds.append([0.0, 0.01])
        else:
            lower = max(0.0, base_val * 0.95)
            upper = base_val * 1.05
            # Ensure upper is greater than lower
            if upper <= lower:
                upper = lower + 0.001
            bounds.append([lower, upper])

    problem = {
        'num_vars': len(param_names),
        'names': np.array(param_names, dtype=object),
        'bounds': bounds
    }

    # Generate samples using Saltelli sampler
    print(f"\nPerforming Sobol sensitivity analysis for {material_name}...")
    print(f"Generating {n_samples * (2 * len(param_names) + 2)} samples...")
    param_values = saltelli.sample(problem, n_samples)

    # Evaluate model for all samples
    Y = np.zeros(param_values.shape[0])
    for i, params in enumerate(param_values):
        # Create parameter dictionary
        test_params = base_params.copy()
        for j, name in enumerate(param_names):
            test_params[name] = params[j]

        # Compute PCI
        Y[i] = compute_pci_for_material(test_params)

    # Perform Sobol analysis
    Si = sobol.analyze(problem, Y)
    # Keep it non negative
    Si['S1'] = np.clip(np.asarray(Si['S1']), 0.0, 1.0)
    Si['ST'] = np.clip(np.asarray(Si['ST']), 0.0, 1.0)
    Si['S1_conf'] = np.nan_to_num(np.asarray(Si['S1_conf']), nan=0.0, posinf=0.0, neginf=0.0)
    Si['ST_conf'] = np.nan_to_num(np.asarray(Si['ST_conf']), nan=0.0, posinf=0.0, neginf=0.0)

    # Print results
    print("\n" + "=" * 70)
    print(f"SENSITIVITY ANALYSIS RESULTS - {material_name}")
    print("=" * 70)
    print("\nFirst-order Sobol indices (S1):")
    print("-" * 70)
    for i, name in enumerate(param_names):
        print(f"{name:<10} S1: {Si['S1'][i]:>8.4f}  (Conf: {Si['S1_conf'][i]:>8.4f})")

    print("\nTotal-order Sobol indices (ST):")
    print("-" * 70)
    for i, name in enumerate(param_names):
        print(f"{name:<10} ST: {Si['ST'][i]:>8.4f}  (Conf: {Si['ST_conf'][i]:>8.4f})")
    print("=" * 70)

           
 # S1 vs ST plotting

    fig, ax = plt.subplots(1, 1, figsize=(16, 10), dpi = 600)

    # Palette (11 params)
    palette = [
        "#67001f",
        "#b2182b",
        "#d6604d",
        "#f4a582",
        "#fddbc7",
        "#f7f7f7",
        "#d1e5f0",
        "#92c5de",
        "#4393c3",
        "#2166ac",
        "#053061"
    ]

    # --- Sort by total-order sensitivity (high → low) ---
    order = np.argsort(np.asarray(Si['ST']))[::-1]   # use 'S1' if you prefer

    # Reorder consistently
    param_names   = [param_names[i] for i in order]
    param_labels  = [PARAM_FULL_NAMES.get(p, p) for p in param_names]
    Si['S1']      = np.asarray(Si['S1'])[order]
    Si['S1_conf'] = np.asarray(Si['S1_conf'])[order]
    Si['ST']      = np.asarray(Si['ST'])[order]
    Si['ST_conf'] = np.asarray(Si['ST_conf'])[order]
    colors        = [palette[i] for i in order]

    n = len(param_names)
    idx = np.arange(n)
    gap = 0.1
    width = 0.35  # bar width for each (S1 and ST)

    # Build asymmetric y-errors so we never go below 0
    S1 = Si['S1']; ST = Si['ST']
    S1_conf = np.nan_to_num(Si['S1_conf'], nan=0.0, posinf=0.0, neginf=0.0)
    ST_conf = np.nan_to_num(Si['ST_conf'], nan=0.0, posinf=0.0, neginf=0.0)


    S1_err_lower = np.minimum(S1_conf, S1)   # not more than the bar height
    S1_err_upper = S1_conf
    ST_err_lower = np.minimum(ST_conf, ST)
    ST_err_upper = ST_conf

    yerr_S1 = np.vstack([S1_err_lower, S1_err_upper])
    yerr_ST = np.vstack([ST_err_lower, ST_err_upper])

    # Bars: S1 (solid) and ST (hatched) side-by-side for each parameter
    bars1 = ax.bar(
        idx - width/2 - gap/2, S1, yerr=yerr_S1,
        width=width, color=colors, edgecolor='black', linewidth=1.5, capsize=4,
        alpha=0.7, label='S1'
    )
    bars2 = ax.bar(
        idx + width/2 + gap/2, ST, yerr=yerr_ST,
        width=width, color=colors, edgecolor='black', linewidth=1.5, capsize=4,
        alpha=0.7, hatch='//', label='ST'
    )
    ax.set_ylim(bottom=0)
    
    # Draw first to get limits for padding
    ax.figure.canvas.draw()
    ylo, yhi = ax.get_ylim()
    pad = 0.015 * (yhi - ylo)

    # Value labels above bars (only for indices >= threshold)
    S1_conf = np.nan_to_num(Si['S1_conf'], nan=0.0)
    ST_conf = np.nan_to_num(Si['ST_conf'], nan=0.0)

    label_threshold = 0.01  # do NOT label bars smaller than this in main plot

    for i, b in enumerate(bars1):
        if b.get_height() >= label_threshold:
            y = b.get_height() + S1_conf[i] + pad
            ax.text(
                b.get_x() + b.get_width()/2, y, f"{b.get_height():.3f}",
                ha='center', va='bottom', fontsize=18, fontweight='bold',
                clip_on=False, zorder=5
            )

    for i, b in enumerate(bars2):
        if b.get_height() >= label_threshold:
            y = b.get_height() + ST_conf[i] + pad
            ax.text(
                b.get_x() + b.get_width()/2, y, f"{b.get_height():.3f}",
                ha='center', va='bottom', fontsize=18, fontweight='bold',
                clip_on=False, zorder=5
            )

    # X axis: same tick per parameter
    ax.set_xticks(idx)
    ax.set_xticklabels(param_labels, rotation=30, ha='right', fontsize=16, fontweight='bold')

    # Cosmetics
    ax.set_ylabel('Sobol Index', fontsize=18)
    ax.tick_params(axis='y', labelsize=18)

    #ax.set_title(f'Sensitivity — {material_name} (S1 solid, ST hatched)', alpha = 0.5, fontsize=16)
    legend_handles = [
        Patch(facecolor='white', edgecolor='black', linewidth=1.5, label='First-order Sobol Index (S1)'),
        Patch(facecolor='white', edgecolor='black', linewidth=1.5, hatch='///', label='Total-order Sobol Index (ST)')
    ]

    # Legend inside a subtle boxed frame
    legend = ax.legend(
        handles=legend_handles,
        loc='upper right',
        frameon=True,
        fontsize=18,
        handlelength=1.6,
        handletextpad=0.8,
        borderpad=0.9,
        labelspacing=0.7
    )

    # Style the legend box
    legend.get_frame().set_edgecolor('black')
    legend.get_frame().set_linewidth(0.8)
    legend.get_frame().set_facecolor('white')
    
    ax.set_ylabel('Sobol Index', fontsize=19, fontweight='bold')
    #ax.set_title(f'Sensitivity — {material_name} (S1 solid, ST hatched)', fontweight='bold', fontsize=16)
    ax.grid(False)

    # ------------------------------------------------------------------
    # Inset axes: zoom on small Sobol indices
    # ------------------------------------------------------------------
    zoom_threshold = 0.01
    small_idx = np.where(ST < zoom_threshold)[0]

    if len(small_idx) > 0:

        inset_ax = inset_axes(
            ax,
            width="75%", height="75%",
            loc="upper left",
            bbox_to_anchor=(0.55, 0.25, 0.5, 0.5),   # RIGHT SIDE under legend
            bbox_transform=ax.transAxes,
            borderpad=1.2
        )


        # Plot small S1 and ST bars only
        inset_ax.bar(
            idx[small_idx] - width/2 - gap/2,
            S1[small_idx],
            yerr=yerr_S1[:, small_idx],
            width=width,
            color=[colors[i] for i in small_idx],
            edgecolor='black',
            linewidth=1.0,
            capsize=3,
            alpha=0.8
        )

        inset_ax.bar(
            idx[small_idx] + width/2 + gap/2,
            ST[small_idx],
            yerr=yerr_ST[:, small_idx],
            width=width,
            color=[colors[i] for i in small_idx],
            edgecolor='black',
            linewidth=1.0,
            capsize=3,
            alpha=0.8,
            hatch='//'
        )

        # Find the max value + error among the zoomed parameters
        max_inset_val = 0.0
        for i in small_idx:
            max_inset_val = max(
                max_inset_val,
                S1[i] + S1_conf[i],
                ST[i] + ST_conf[i]
            )

        # Add a small headroom (10–20%)
        inset_ax.set_ylim(0, max_inset_val * 1.2)

        # --------------------------------------------
        # Add numeric labels above bars in inset
        # --------------------------------------------
        for j, i in enumerate(small_idx):
            # positions for S1 and ST bars in inset
            x_s1 = idx[i] - width/2 - gap/2
            x_st = idx[i] + width/2 + gap/2

            # heights + error for placement
            y_s1 = S1[i] + S1_conf[i]
            y_st = ST[i] + ST_conf[i]

            # small padding relative to inset y-axis height
            pad = (inset_ax.get_ylim()[1] - inset_ax.get_ylim()[0]) * 0.03

            # S1 label
            inset_ax.text(
                x_s1,
                y_s1 + pad,
                f"{S1[i]:.3f}",
                ha='center',
                va='bottom',
                fontsize=14,
                fontweight='bold'
            )

            # ST label
            inset_ax.text(
                x_st,
                y_st + pad,
                f"{ST[i]:.3f}",
                ha='center',
                va='bottom',
                fontsize=14,
                fontweight='bold'
            )
            
        # -----------------------------------------------------------
        # Custom dashed rectangle around the zoomed region (tighter)
        # -----------------------------------------------------------

        # X-range of the small bars we are zooming on
        x0 = idx[small_idx[0]] - 0.6
        x1 = idx[small_idx[-1]] + 0.6

        # Y-range of the zoom box in the main plot
        # (shrink rect_y1 a bit compared to zoom_threshold*1.15 if needed)
        rect_y0 = 0.0
        rect_y1 = zoom_threshold * 1.6   # slightly above the max of the inset

        # Create a bbox in DATA coordinates of the main axes
        rect_data_bbox = Bbox.from_extents(x0, rect_y0, x1, rect_y1)
        rect = TransformedBbox(rect_data_bbox, ax.transData)

        # Dashed rectangle (tighter box)
        pp = BboxPatch(
            rect,
            fill=False,
            edgecolor="black",
            linestyle="--",
            linewidth=0.9,
            alpha=0.4
        )
        ax.add_patch(pp)

        # Connector lines between inset and dashed rectangle
        p1 = BboxConnector(
            inset_ax.bbox, rect,
            loc1=2, loc2=2,      # top-left to top-left
            linestyle="--",
            linewidth=0.9,
            edgecolor="black",
            alpha=0.4
        )
        p2 = BboxConnector(
            inset_ax.bbox, rect,
            loc1=4, loc2=4,      # bottom-right to bottom-right
            linestyle="--",
            linewidth=0.9,
            edgecolor="black",
            alpha=0.4
        )
        ax.add_patch(p1)
        ax.add_patch(p2)

        # Remove x-axis tick labels completely
        inset_ax.set_xticks([])
        inset_ax.set_xticklabels([])
        inset_ax.tick_params(axis='x', bottom=False)

        #inset_ax.set_ylabel("Sobol Index", fontsize=10)
        inset_ax.tick_params(axis='y', labelsize=9)
        #inset_ax.set_title("Zoom on small indices", fontsize=10)
        inset_ax.grid(False)
    # Remove top and right border
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(save_path, dpi=600, bbox_inches='tight')
    print(f"\nSensitivity analysis plot saved to: {save_path}")
    plt.show()

    return Si


def tornado_plot(csv_file='pci_material_parameters.csv', material_name=None,
                 variation_pct=0.05, save_path='pci_tornado.png', dpi=300, figsize=(12, 7)):
    """
    Create a tornado plot showing the impact of parameter variations on PCI.

    Args:
        csv_file: Path to the CSV file containing material parameters
        material_name: Specific material to analyze (if None, analyzes first material)
        variation_pct: Percentage variation to apply (e.g., 0.05 = ±5%)
        save_path: Path to save the figure
        dpi: Resolution for saved figure
        figsize: Figure size (width, height) in inches

    Returns:
        Dictionary containing parameter impacts
    """
    # Load material parameters
    materials, Total_EVB_Mass = load_material_parameters(csv_file)

    # Select material to analyze
    if material_name is None:
        material_name = list(materials.keys())[0]

    if material_name not in materials:
        raise ValueError(f"Material {material_name} not found in CSV")

    base_params = materials[material_name]
    base_pci = compute_pci_for_material(base_params)

    # Define parameters to analyze
    param_names = ['F_u', 'F_r', 'C_u', 'C_r', 'E_cp', 'E_fp', 'C_fp', 'C_cp', 'E_ms', 'E_rfp', 'X']

    # Calculate impact of each parameter
    impacts = {}

    for param in param_names:
        base_val = base_params[param]

        # Test with +variation
        test_params_high = base_params.copy()
        if base_val == 0 or abs(base_val) < 1e-10:
            test_params_high[param] = 0.01
        else:
            test_params_high[param] = base_val * (1 + variation_pct)
        pci_high = compute_pci_for_material(test_params_high)

        # Test with -variation
        test_params_low = base_params.copy()
        if base_val == 0 or abs(base_val) < 1e-10:
            test_params_low[param] = 0.0
        else:
            test_params_low[param] = max(0, base_val * (1 - variation_pct))
        pci_low = compute_pci_for_material(test_params_low)

        # Store impacts
        impacts[param] = {
            'base': base_pci,
            'low': pci_low,
            'high': pci_high,
            'impact_low': pci_low - base_pci,
            'impact_high': pci_high - base_pci,
            'range': abs(pci_high - pci_low)
        }

    # Sort parameters by total impact (range)
    sorted_params = sorted(impacts.items(), key=lambda x: x[1]['range'], reverse=True)

    # Create tornado plot
    sns.set_style("whitegrid")
    sns.set_context("paper", font_scale=1.3)

    fig, ax = plt.subplots(figsize=figsize)

    # Prepare data for plotting
    param_short_names = [p[0] for p in sorted_params]
    # Convert to full descriptive names
    param_labels = [PARAM_FULL_NAMES.get(p, p) for p in param_short_names]
    low_impacts = [p[1]['impact_low'] for p in sorted_params]
    high_impacts = [p[1]['impact_high'] for p in sorted_params]

    y_pos = np.arange(len(param_labels))

    # Create horizontal bars
    bars_low = ax.barh(y_pos, low_impacts, height=0.4, align='center',
                       color='#dfc27d', alpha=1, label=f'-{variation_pct*100}%')
    bars_high = ax.barh(y_pos, high_impacts, height=0.4, align='center',
                        color='#80cdc1', alpha=1, label=f'+{variation_pct*100}%')

    # Add vertical line at base PCI
    ax.axvline(x=0, color='black', linestyle='-', linewidth=1.5)

    # Customize plot
    ax.set_yticks(y_pos)
    ax.set_yticklabels(param_labels, fontsize=8, fontweight='bold')
    ax.set_xlabel('Change in PCI', fontsize=13)
    ax.set_title(f'Tornado Plot: Parameter Sensitivity - {material_name}\n(Base PCI: {base_pci:.4f}, ±{variation_pct*100}% variation)',
                 fontweight='bold', fontsize=13, pad=20)

    # Add value labels on bars
    for i, (low, high) in enumerate(zip(low_impacts, high_impacts)):
        # Label for low impact
        if abs(low) > 0.001:
            ax.text(low, i, f' {low:.3f}', ha='right' if low < 0 else 'left',
                   va='center', fontsize=9, fontweight='bold')
        # Label for high impact
        if abs(high) > 0.001:
            ax.text(high, i, f' {high:.3f}', ha='left' if high > 0 else 'right',
                   va='center', fontsize=9, fontweight='bold')

    # Add grid
    ax.grid(False)
    ax.set_axisbelow(False)

    # Add legend
    ax.legend(loc='best', frameon=True, fontsize=13)

    plt.tight_layout()
    plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
    print(f"\nTornado plot saved to: {save_path}")
    plt.show()

    # Print impact summary
    print("\n" + "=" * 70)
    print(f"TORNADO ANALYSIS RESULTS - {material_name}")
    print("=" * 70)
    print(f"Base PCI: {base_pci:.4f}")
    print(f"\nParameter impacts (sorted by total range, ±{variation_pct*100}% variation):")
    print("-" * 70)
    print(f"{'Parameter':<12} {'Low Impact':<15} {'High Impact':<15} {'Total Range':<15}")
    print("-" * 70)
    for param, data in sorted_params:
        print(f"{param:<12} {data['impact_low']:>14.4f} {data['impact_high']:>14.4f} {data['range']:>14.4f}")
    print("=" * 70)

    return impacts, sorted_params


if __name__ == '__main__':
    """
    MONTE CARLO SIMULATION PARAMETERS:
    - Distribution: Normal (Gaussian)
    - Uncertainty: 5% of parameter value (std_dev = 0.05 * value)
    - Samples: 1000
    - Confidence Level: 95% (alpha = 0.05)
    - Method: Percentile-based confidence intervals
    - Constraints: Non-negative values for masses and efficiencies,
                   Fractions clipped to [0, 1]

    SENSITIVITY ANALYSIS PARAMETERS:
    - Method: Sobol variance-based sensitivity analysis
    - Variation: ±5% around base values
    - Sampler: Saltelli (quasi-random sampling)
    - Indices: First-order (S1) and Total-order (ST)
    """

    # Set default parameters
    confidence_level = 0.95

    # ============================================================
    # RUN ONLY THE LFP SOLID CASE
    # The CSV must be in the same folder as this script:
    # pci_material_parameters_solid.csv
    # ============================================================
    SUF = '_solid'
    csv_file = 'pci_material_parameters_solid.csv'

    # 1. Print PCI results
    print("\n" + "="*70)
    print("TASK 1: PRINTING PCI RESULTS")
    print("="*70)
    final_pci, material_pcis = print_pci_results(csv_file)

    # 2. Create basic bar plot
    print("\n" + "="*70)
    print("TASK 2: CREATING JOURNAL-QUALITY BAR PLOT")
    print("="*70)
    plot_pci_bar_chart(csv_file=csv_file, save_path=f'pci_bar_chart{SUF}.png')

    # 3. Monte Carlo with error bars
    print("\n" + "="*70)
    print("TASK 3: MONTE CARLO SIMULATION WITH ERROR BARS")
    print("="*70)
    print("Monte Carlo Parameters:")
    print("  - Distribution: Normal (Gaussian)")
    print("  - Uncertainty: 5% std dev of parameter values")
    print("  - Samples: 1000")
    print("  - Confidence: 95%")
    fig, ax, stats = plot_pci_with_error_bars(csv_file=csv_file, n_samples=1000,
                                              uncertainty_pct=0.05,
                                              save_path=f'pci_with_error_bars{SUF}.png')

    # Save cumulative PCI results to common CSV
    import csv
    import os
    cumulative_csv_path = os.path.join('..', f'cumulative_results_indicators{SUF}.csv')

    # Extract weighted PCI stats
    if 'FINAL_PCI' in stats:
        pci_mean = stats['FINAL_PCI']['mean']
        pci_lower = stats['FINAL_PCI']['lower_ci']
        pci_upper = stats['FINAL_PCI']['upper_ci']

        # Check if file exists to determine if we need headers
        file_exists = os.path.exists(cumulative_csv_path)

        # Read existing data if file exists
        existing_data = {}
        if file_exists:
            with open(cumulative_csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_data[row['Indicator']] = row

        # Update with PCI data
        existing_data['PCI'] = {
            'Indicator': 'PCI',
            'Mean': f'{pci_mean:.6f}',
            'CI_Lower': f'{pci_lower:.6f}',
            'CI_Upper': f'{pci_upper:.6f}'
        }

        # Write back to CSV
        with open(cumulative_csv_path, 'w', newline='') as f:
            fieldnames = ['Indicator', 'Mean', 'CI_Lower', 'CI_Upper']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for indicator in ['PCI', 'CI', 'CEI', 'ECPI']:
                if indicator in existing_data:
                    writer.writerow(existing_data[indicator])

        print(f"\nPCI results saved to {cumulative_csv_path}")

    # 4. Tornado plots (one-at-a-time sensitivity)
    print("\n" + "="*70)
    print("TASK 4: TORNADO PLOTS (±5% VARIATION)")
    print("="*70)

    # Create tornado plots for each material
    materials, _ = load_material_parameters(csv_file)
    for material in materials.keys():
        save_path = f'pci_tornado_{material.replace(" ", "_")}{SUF}.png'
        impacts, sorted_params = tornado_plot(csv_file=csv_file, material_name=material, variation_pct=0.05,
                                              save_path=save_path)
        print("\n")

    # 5. Sobol global sensitivity analysis
    print("\n" + "="*70)
    print("TASK 5: SOBOL GLOBAL SENSITIVITY ANALYSIS (±5% VARIATION)")
    print("="*70)

    # Perform Sobol analysis for each material
    for material in materials.keys():
        save_path = f'pci_sobol_{material.replace(" ", "_")}{SUF}.png'
        Si = sensitivity_analysis(csv_file=csv_file, material_name=material, n_samples=512, save_path=save_path)
        print("\n")

    print("\n" + "="*70)
    print("ALL TASKS COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("\nGenerated files:")
    print("  - pci_bar_chart_solid.png (basic bar plot)")
    print("  - pci_with_error_bars_solid.png (Monte Carlo error bars)")
    print("  - pci_tornado_*_solid.png (tornado plots for each material)")
    print("  - pci_sobol_*_solid.png (Sobol sensitivity plots for each material)")
    print("  - cumulative_results_indicators_solid.csv")
    print("="*70)
