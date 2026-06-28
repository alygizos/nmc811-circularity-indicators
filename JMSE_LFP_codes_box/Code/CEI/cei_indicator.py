import csv
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def load_battery_materials_data(csv_path='cei_parameters.csv'):
    """
    Load battery materials data from CSV file.

    Parameters
    ----------
    csv_path : str
        Path to the CSV file containing material data

    Returns
    -------
    list of dict
        List of material dictionaries with keys:
        - material_name
        - mass_required
        - mass_recycled
        - price_primary
        - price_recycled
    """
    materials = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            materials.append({
                'material_name': row['material_name'],
                'mass_required': float(row['mass_required_kg']),
                'mass_recycled': float(row['mass_recycled_kg']),
                'price_primary': float(row['price_virgin_usd_per_kg']),
                'price_recycled': float(row['price_recycled_usd_per_kg'])
            })

    return materials

def compute_cei_di_maio(materials):
    """
    Circular Economy Index (CEI) from Di Maio & Rem (2015)
    Uses economic allocation (mass × price).

    Parameters
    ----------
    materials : list of dict
        Each dict must contain:
        {
            'mass_required': float,    # kg needed to reproduce product
            'mass_recycled': float,    # kg recycled entering process
            'price_primary': float,    # $/kg virgin
            'price_recycled': float    # $/kg recycled
        }

    Returns
    -------
    float
        CEI value between 0 and 1
    """
    V_recycled = sum(m['mass_recycled'] * m['price_recycled'] for m in materials)
    V_required = sum(m['mass_required'] * m['price_primary'] for m in materials)
    if V_required == 0:
        return 0.0
    cei = V_recycled / V_required
    return max(0.0, min(cei, 1.0))

def print_cei_details(materials, cei_value):
    """
    Print detailed breakdown of CEI calculation.

    Parameters
    ----------
    materials : list of dict
        Material data
    cei_value : float
        Computed CEI value
    """
    print("\n" + "="*80)
    print("CEI Calculation Details (Economic Allocation)")
    print("="*80)

    print(f"\n{'Material':<15} {'Mass Req (kg)':<15} {'Mass Rec (kg)':<15} "
          f"{'Price Virgin':<15} {'Price Recycled':<15}")
    print("-"*80)

    total_mass_required = 0
    V_required_total = 0
    V_recycled_total = 0

    for m in materials:
        print(f"{m.get('material_name', 'N/A'):<15} "
              f"{m['mass_required']:<15.4f} "
              f"{m['mass_recycled']:<15.4f} "
              f"${m['price_primary']:<14.2f} "
              f"${m['price_recycled']:<14.2f}")

        total_mass_required += m['mass_required']
        V_required_total += m['mass_required'] * m['price_primary']
        V_recycled_total += m['mass_recycled'] * m['price_recycled']

    print("-"*80)
    print(f"{'TOTAL':<15} {total_mass_required:<15.4f}")
    print("="*80)

    print(f"\nTotal Economic Value (Virgin):   ${V_required_total:,.2f}")
    print(f"Total Economic Value (Recycled): ${V_recycled_total:,.2f}")
    print(f"\nCEI (Circular Economy Index):    {cei_value:.4f}")
    print(f"CEI Percentage:                   {cei_value*100:.2f}%")
    print("="*80 + "\n")


def plot_cei_bar_chart(cei_value, save_path='cei_bar_chart.png', dpi=300, figsize=(6, 6)):
    """
    Create journal-quality bar plot for CEI (cumulative result).

    Parameters
    ----------
    cei_value : float
        Computed CEI value
    save_path : str
        Path to save figure
    dpi : int
        Resolution
    figsize : tuple
        Figure size
    """
    # Set publication-quality style
    sns.set_style("whitegrid")
    sns.set_context("paper", font_scale=1.5)

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Create bar
    colors = ['#2ecc71']  # Green color for CEI
    bars = ax.bar([0], [cei_value], color=colors, edgecolor='black',
                   linewidth=1.2, alpha=0.8, width=0.5)

    # Customize plot
    ax.set_ylabel('Circular Economy Index (CEI)', fontweight='bold', fontsize=14)
    ax.set_title('Circular Economy Index\n(Economic Allocation)',
                 fontweight='bold', fontsize=16, pad=20)

    # Set x-axis
    ax.set_xticks([0])
    ax.set_xticklabels(['Cumulative CEI'])

    # Add value label on top of bar
    height = bars[0].get_height()
    ax.text(0, height, f'{cei_value:.4f}\n({cei_value*100:.2f}%)',
            ha='center', va='bottom', fontsize=12, fontweight='bold')

    # Add grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    # Set y-axis limits
    ax.set_ylim(0, max(1.0, cei_value * 1.15))

    plt.tight_layout()
    plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
    print(f"\nCEI bar chart saved to: {save_path}")
    plt.show()

    return fig, ax


def monte_carlo_cei(csv_path='cei_parameters.csv', n_samples=1000,
                    uncertainty_pct=0.05, confidence_level=0.95):
    """
    Perform Monte Carlo simulation for CEI uncertainty analysis.
    Varies price_virgin and price_recycled parameters.

    Parameters
    ----------
    csv_path : str
        Path to CSV file
    n_samples : int
        Number of MC samples
    uncertainty_pct : float
        Uncertainty percentage (0.05 = 5%)
    confidence_level : float
        Confidence level (0.95 = 95%)

    Returns
    -------
    dict
        Statistics for CEI
    """
    # Load base materials
    base_materials = load_battery_materials_data(csv_path)

    # Storage for results
    mc_results = []

    # Monte Carlo sampling
    for _ in range(n_samples):
        perturbed_materials = []

        for mat in base_materials:
            perturbed_mat = mat.copy()

            # Perturb price_virgin
            std_dev = abs(mat['price_primary'] * uncertainty_pct)
            perturbed_price_virgin = max(0.01, np.random.normal(mat['price_primary'], std_dev))
            perturbed_mat['price_primary'] = perturbed_price_virgin

            # Perturb price_recycled
            std_dev = abs(mat['price_recycled'] * uncertainty_pct)
            perturbed_price_recycled = max(0.01, np.random.normal(mat['price_recycled'], std_dev))
            perturbed_mat['price_recycled'] = perturbed_price_recycled

            perturbed_materials.append(perturbed_mat)

        # Compute CEI with perturbed parameters
        cei = compute_cei_di_maio(perturbed_materials)
        mc_results.append(cei)

    # Calculate statistics
    alpha = 1 - confidence_level
    values_array = np.array(mc_results)
    mean_val = np.mean(values_array)
    std_val = np.std(values_array)
    lower_ci = np.percentile(values_array, alpha/2 * 100)
    upper_ci = np.percentile(values_array, (1 - alpha/2) * 100)

    stats = {
        'mean': mean_val,
        'std': std_val,
        'lower_ci': lower_ci,
        'upper_ci': upper_ci,
        'error_bar': (mean_val - lower_ci, upper_ci - mean_val)
    }

    return stats, mc_results


def plot_cei_with_error_bars(csv_path='cei_parameters.csv', n_samples=1000,
                             uncertainty_pct=0.05, save_path='cei_with_error_bars.png',
                             dpi=300, figsize=(6, 6)):
    """
    Create CEI bar plot with Monte Carlo error bars.

    Parameters
    ----------
    csv_path : str
        Path to CSV file
    n_samples : int
        Number of MC samples
    uncertainty_pct : float
        Uncertainty percentage
    save_path : str
        Path to save figure
    dpi : int
        Resolution
    figsize : tuple
        Figure size
    """
    print(f"\nRunning Monte Carlo simulation with {n_samples} samples...")
    stats, mc_results = monte_carlo_cei(csv_path, n_samples, uncertainty_pct)

    # Set style
    sns.set_style("whitegrid")
    sns.set_context("paper", font_scale=1.5)

    fig, ax = plt.subplots(figsize=figsize)

    # Prepare data
    mean = stats['mean']
    error_lower = stats['error_bar'][0]
    error_upper = stats['error_bar'][1]

    # Create color
    colors = ['#2ecc71']  # Green

    # Create bar plot with error bars
    bars = ax.bar([0], [mean], color=colors, edgecolor='black',
                   linewidth=1.2, alpha=0.8, width=0.5)
    ax.errorbar([0], [mean], yerr=[[error_lower], [error_upper]],
                fmt='none', ecolor='black', capsize=5, capthick=2, linewidth=2)

    # Customize plot
    ax.set_ylabel('Circular Economy Index (CEI)', fontweight='bold', fontsize=14)
    ax.set_title(f'CEI with 95% Confidence Intervals\n(Monte Carlo: {n_samples} samples, {uncertainty_pct*100}% uncertainty)',
                 fontweight='bold', fontsize=14, pad=20)

    # Set x-axis
    ax.set_xticks([0])
    ax.set_xticklabels(['Cumulative CEI'])

    # Add value label
    ax.text(0, mean, f'{mean:.4f}\n({mean*100:.2f}%)',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

    # Add grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    # Set y-axis limits
    ax.set_ylim(0, max(1.0, mean * 1.2))

    plt.tight_layout()
    plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
    print(f"CEI bar chart with error bars saved to: {save_path}")
    plt.show()

    # Print statistics
    print("\n" + "=" * 70)
    print("MONTE CARLO SIMULATION RESULTS")
    print("=" * 70)
    print(f"\nCumulative CEI:")
    print(f"  Mean CEI:    {stats['mean']:.6f}")
    print(f"  Std Dev:     {stats['std']:.6f}")
    print(f"  95% CI:      [{stats['lower_ci']:.6f}, {stats['upper_ci']:.6f}]")
    print(f"  Percentage:  {stats['mean']*100:.2f}% ± {stats['std']*100:.2f}%")
    print("=" * 70)

    return fig, ax, stats


def tornado_plot_cei(csv_path='cei_parameters.csv', variation_pct=0.05,
                    save_path='cei_tornado.png', dpi=300, figsize=(10, 6)):
    """
    Create tornado plot for CEI sensitivity analysis on prices.

    Parameters
    ----------
    csv_path : str
        Path to CSV file
    variation_pct : float
        Percentage variation (±5%)
    save_path : str
        Path to save figure
    dpi : int
        Resolution
    figsize : tuple
        Figure size
    """
    # Load base materials
    base_materials = load_battery_materials_data(csv_path)

    # Compute base CEI
    base_cei = compute_cei_di_maio(base_materials)

    # Parameters to analyze
    param_names = ['price_virgin', 'price_recycled']

    impacts = {}

    for param in param_names:
        # High variation
        modified_materials_high = []
        for mat in base_materials:
            mod_mat = mat.copy()
            if param == 'price_virgin':
                mod_mat['price_primary'] = mat['price_primary'] * (1 + variation_pct)
            else:  # price_recycled
                mod_mat['price_recycled'] = mat['price_recycled'] * (1 + variation_pct)
            modified_materials_high.append(mod_mat)

        cei_high = compute_cei_di_maio(modified_materials_high)

        # Low variation
        modified_materials_low = []
        for mat in base_materials:
            mod_mat = mat.copy()
            if param == 'price_virgin':
                mod_mat['price_primary'] = max(0.01, mat['price_primary'] * (1 - variation_pct))
            else:  # price_recycled
                mod_mat['price_recycled'] = max(0.01, mat['price_recycled'] * (1 - variation_pct))
            modified_materials_low.append(mod_mat)

        cei_low = compute_cei_di_maio(modified_materials_low)

        impacts[param] = {
            'base': base_cei,
            'low': cei_low,
            'high': cei_high,
            'impact_low': cei_low - base_cei,
            'impact_high': cei_high - base_cei,
            'range': abs(cei_high - cei_low)
        }

    # Sort by impact
    sorted_params = sorted(impacts.items(), key=lambda x: x[1]['range'], reverse=True)

    # Create tornado plot
    sns.set_style("whitegrid")
    sns.set_context("paper", font_scale=1.3)

    fig, ax = plt.subplots(figsize=figsize)

    # Prepare data
    param_labels = [p[0].replace('_', ' ').title() for p in sorted_params]
    low_impacts = [p[1]['impact_low'] for p in sorted_params]
    high_impacts = [p[1]['impact_high'] for p in sorted_params]

    y_pos = np.arange(len(param_labels))

    # Create horizontal bars
    bars_low = ax.barh(y_pos, low_impacts, height=0.4, align='center',
                       color='#d73027', alpha=0.8, label=f'-{variation_pct*100}%')
    bars_high = ax.barh(y_pos, high_impacts, height=0.4, align='center',
                        color='#4575b4', alpha=0.8, label=f'+{variation_pct*100}%')

    # Add vertical line at base
    ax.axvline(x=0, color='black', linestyle='-', linewidth=2)

    # Customize
    ax.set_yticks(y_pos)
    ax.set_yticklabels(param_labels)
    ax.set_xlabel('Change in CEI', fontweight='bold', fontsize=14)
    ax.set_title(f'Tornado Plot: CEI Price Sensitivity\n(Base CEI: {base_cei:.4f}, ±{variation_pct*100}% variation)',
                 fontweight='bold', fontsize=14, pad=20)

    # Add value labels
    for i, (low, high) in enumerate(zip(low_impacts, high_impacts)):
        if abs(low) > 0.001:
            ax.text(low, i, f' {low:.4f}', ha='right' if low < 0 else 'left',
                   va='center', fontsize=10, fontweight='bold')
        if abs(high) > 0.001:
            ax.text(high, i, f' {high:.4f}', ha='left' if high > 0 else 'right',
                   va='center', fontsize=10, fontweight='bold')

    # Grid
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    # Legend
    ax.legend(loc='best', frameon=True, shadow=True, fontsize=11)

    plt.tight_layout()
    plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
    print(f"\nTornado plot saved to: {save_path}")
    plt.show()

    # Print results
    print("\n" + "=" * 70)
    print("TORNADO ANALYSIS RESULTS - CEI")
    print("=" * 70)
    print(f"Base CEI: {base_cei:.6f}")
    print(f"\nParameter impacts (±{variation_pct*100}% variation):")
    print("-" * 70)
    print(f"{'Parameter':<20} {'Low Impact':<15} {'High Impact':<15} {'Range':<15}")
    print("-" * 70)
    for param, data in sorted_params:
        print(f"{param:<20} {data['impact_low']:>14.6f} {data['impact_high']:>14.6f} {data['range']:>14.6f}")
    print("=" * 70)

    return impacts, sorted_params


if __name__ == "__main__":
    """
    CEI Analysis with visualization and uncertainty quantification.

    MONTE CARLO PARAMETERS:
    - Distribution: Normal (Gaussian)
    - Uncertainty: 5% std dev of price values
    - Samples: 1000
    - Confidence: 95%
    - Parameters varied: price_virgin, price_recycled

    SENSITIVITY ANALYSIS PARAMETERS:
    - Variation: ±5% around base values
    - Parameters: price_virgin, price_recycled
    """
    # Load materials from CSV (route-separated: hydro -> canonical, solid -> *_solid)
    SUF = '_solid' if os.environ.get('LFP_ROUTE') == 'solid' else ''
    csv_file = f'cei_parameters{SUF}.csv'

    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        print("Please ensure the CSV file is in the same directory as this script.")
    else:
        # Task 1: Compute and print results
        print("\n" + "="*70)
        print("TASK 1: COMPUTING AND PRINTING CEI RESULTS")
        print("="*70)

        materials = load_battery_materials_data(csv_file)
        cei = compute_cei_di_maio(materials)
        print_cei_details(materials, cei)

        # Task 2: Create bar plot
        print("\n" + "="*70)
        print("TASK 2: CREATING BAR PLOT")
        print("="*70)
        plot_cei_bar_chart(cei, save_path=f'cei_bar_chart{SUF}.png')

        # Task 3: Monte Carlo with error bars
        print("\n" + "="*70)
        print("TASK 3: MONTE CARLO SIMULATION WITH ERROR BARS")
        print("="*70)
        print("Monte Carlo Parameters:")
        print("  - Distribution: Normal (Gaussian)")
        print("  - Uncertainty: 5% std dev on prices")
        print("  - Samples: 1000")
        print("  - Confidence: 95%")
        print("  - Parameters: price_virgin, price_recycled")
        fig, ax, stats = plot_cei_with_error_bars(csv_path=csv_file, n_samples=1000,
                                                  uncertainty_pct=0.05,
                                                  save_path=f'cei_with_error_bars{SUF}.png')

        # Save cumulative CEI results to common CSV
        import csv
        cumulative_csv_path = os.path.join('..', f'cumulative_results_indicators{SUF}.csv')

        # Extract CEI stats
        cei_mean = stats['mean']
        cei_lower = stats['lower_ci']
        cei_upper = stats['upper_ci']

        # Check if file exists to determine if we need headers
        file_exists = os.path.exists(cumulative_csv_path)

        # Read existing data if file exists
        existing_data = {}
        if file_exists:
            with open(cumulative_csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_data[row['Indicator']] = row

        # Update with CEI data
        existing_data['CEI'] = {
            'Indicator': 'CEI',
            'Mean': f'{cei_mean:.6f}',
            'CI_Lower': f'{cei_lower:.6f}',
            'CI_Upper': f'{cei_upper:.6f}'
        }

        # Write back to CSV
        with open(cumulative_csv_path, 'w', newline='') as f:
            fieldnames = ['Indicator', 'Mean', 'CI_Lower', 'CI_Upper']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for indicator in ['PCI', 'CI', 'CEI', 'ECPI']:
                if indicator in existing_data:
                    writer.writerow(existing_data[indicator])

        print(f"\nCEI results saved to {cumulative_csv_path}")

        # Task 4: Tornado plot for sensitivity analysis
        print("\n" + "="*70)
        print("TASK 4: TORNADO PLOT (±5% PRICE VARIATION)")
        print("="*70)
        impacts, sorted_params = tornado_plot_cei(csv_path=csv_file, variation_pct=0.05,
                                                  save_path=f'cei_tornado{SUF}.png')

        print("\n" + "="*70)
        print("ALL TASKS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nGenerated files:")
        print("  - cei_bar_chart.png (basic bar plot)")
        print("  - cei_with_error_bars.png (Monte Carlo error bars)")
        print("  - cei_tornado.png (price sensitivity tornado plot)")
        print("="*70)