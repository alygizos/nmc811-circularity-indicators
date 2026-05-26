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
from indicators import compute_ci_cullen

# csv_dataloading
def load_parameters_from_csv(csv_path='ci_parameters.csv'):
    """
    Load CI parameters from CSV file.

    Parameters
    ----------
    csv_path : str
        Path to the CSV file containing parameters. Default is 'ci_parameters.csv'
        in the current directory.

    Returns
    -------
    dict
        Dictionary with material names as keys and parameter dictionaries as values.
        Example:
        {
            'steel': {'mass': 28.95, 'recycling_efficiency': 0.95, ...},
            'aluminum': {...},
            'cell_total': {...},
            'cell_material_LiOH': {...},
            ...
        }
    """
    # If path is relative, make it relative to this script's directory
    if not os.path.isabs(csv_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, csv_path)

    parameters = {}

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            material = row['material']

            # Skip comment lines (starting with #)
            if material.startswith('#'):
                continue

            params = {}

            # Convert numeric values, keeping empty strings as None
            for key, value in row.items():
                if key == 'material':
                    continue
                if value.strip() == '':
                    params[key] = None
                else:
                    try:
                        params[key] = float(value)
                    except ValueError:
                        params[key] = value

            parameters[material] = params

    return parameters


def get_cell_materials_data_from_csv(csv_path='ci_parameters.csv'):
    """
    Extract cell materials data from CSV for mass allocation method.

    Parameters
    ----------
    csv_path : str
        Path to the CSV file containing parameters.

    Returns
    -------
    list of dict
        List of dictionaries formatted for compute_ci_cell_method3.
    """
    params = load_parameters_from_csv(csv_path)

    materials_data = []
    for material_name, data in params.items():
        if material_name.startswith('cell_material_'):
            # Extract the short name (e.g., 'LiOH' from 'cell_material_LiOH')
            short_name = material_name.replace('cell_material_', '')
            materials_data.append({
                'name': short_name,
                'mass_kg': data['mass'],
                'energy_primary': data['energy_virgin'],
                'recovery_rate': data['recovery_rate']
            })

    return materials_data


# ==========================================================================================================================================================================
# ========================================================================= MATERIAL-SPECIFIC CI FUNCTIONS ===============================================================

def compute_ci_steel(mass, recovery_rate, energy_virgin, energy_recycling):
    alpha = recovery_rate
    beta = 1 - (energy_recycling / energy_virgin)
    return compute_ci_cullen(alpha=alpha, beta=beta)


def compute_ci_aluminum(mass, recovery_rate, energy_virgin, energy_recycling):
    alpha = recovery_rate
    beta = 1 - (energy_recycling / energy_virgin)
    return compute_ci_cullen(alpha=alpha, beta=beta)


def compute_ci_cell_method1(total_cell_mass, total_energy_raw, total_energy_recycling, total_recovered):
    """
    Compute CI for battery cell using Method 1: Energy-based.

    Parameters
    ----------
    total_cell_mass : float
        Total cell mass [kg]
    total_energy_raw : float
        Total energy for raw materials [kWh]
    total_energy_recycling : float
        Total energy for recycling [kWh]
    total_recovered : float
        Total recovered material [kg]

    Returns
    -------
    float
        Circularity Index for cell (energy-based)
    """
    alpha = total_recovered / total_cell_mass
    beta = 1 - (total_energy_recycling / total_energy_raw)
    return compute_ci_cullen(alpha=alpha, beta=beta)


def compute_ci_cell_method2(total_cell_mass, total_energy_recycling, total_recovered, total_adp):
    """
    Compute CI for battery cell using Method 2: ADP-based.

    Parameters
    ----------
    total_cell_mass : float
        Total cell mass [kg]
    total_energy_recycling : float
        Total energy for recycling [kWh]
    total_recovered : float
        Total recovered material [kg]
    total_adp : float
        Total ADP fossil (CML 2016) [MJ/kg]

    Returns
    -------
    float
        Circularity Index for cell (ADP-based)
    """
    alpha = total_recovered / total_cell_mass
    beta = 1 - (total_energy_recycling / total_adp)
    return compute_ci_cullen(alpha=alpha, beta=beta)


def compute_ci_cell_method3(materials_data, total_recycling_energy):
    """
    Compute CI for battery cell using Method 3: Mass allocation.

    Parameters
    ----------
    materials_data : list of dict
        List of dictionaries containing material data:
        - 'name': Material name
        - 'mass_kg': Material mass [kg]
        - 'energy_primary': Energy cost for raw material [kWh]
        - 'recovery_rate': Recovery rate (0-1)
    total_recycling_energy : float
        Total recycling energy [kWh] to be allocated across materials

    Returns
    -------
    dict
        Dictionary with:
        - 'ci_by_material': dict of CI values for each material
        - 'weighted_ci': overall weighted CI
    """
    # Calculate total recovered mass for allocation
    total_recovered_mass = sum(mat['mass_kg'] * mat['recovery_rate'] for mat in materials_data)

    ci_by_material = {}
    total_weighted_ci = 0
    total_mass = 0

    for material in materials_data:
        name = material['name']
        mass = material['mass_kg']
        energy_prim = material['energy_primary']
        recovery_rate = material['recovery_rate']
        recovered_mass = mass * recovery_rate

        # Allocate recycling energy based on recovered mass
        energy_recov = total_recycling_energy * (recovered_mass / total_recovered_mass) if total_recovered_mass > 0 else 0

        # Calculate CI for this material
        # CI = (recovered/total) * (1 - energy_recov/energy_prim)
        alpha = recovery_rate
        beta = 1 - (energy_recov / energy_prim)
        ci = compute_ci_cullen(alpha=alpha, beta=beta)

        ci_by_material[name] = ci
        total_weighted_ci += ci * mass
        total_mass += mass

    # Calculate overall weighted CI
    weighted_ci = total_weighted_ci / total_mass if total_mass > 0 else 0

    return {
        'ci_by_material': ci_by_material,
        'weighted_ci': weighted_ci
    }

# ========================================================================= CSV-BASED CI FUNCTIONS =======================================================================

def compute_all_ci_from_csv(csv_path='ci_parameters.csv'):
    """
    Compute all CI values using parameters from CSV file.

    Parameters
    ----------
    csv_path : str
        Path to the CSV file containing parameters.

    Returns
    -------
    dict
        Dictionary containing all CI calculations:
        - 'steel_ci': Circularity Index for steel
        - 'aluminum_ci': Circularity Index for aluminum
        - 'cell_ci_method1': Cell CI using Method 1 (energy-based)
        - 'cell_ci_method2': Cell CI using Method 2 (ADP-based)
        - 'cell_ci_method3': Cell CI using Method 3 (mass allocation) - dict with ci_by_material and weighted_ci
        - 'total_ci_method1': Combined CI using Method 1 (energy-based)
        - 'total_ci_method2': Combined CI using Method 2 (ADP-based)
        - 'total_ci_method3': Combined CI using Method 3 (mass allocation)
        - 'parameters': Dictionary of loaded parameters
    """
    params = load_parameters_from_csv(csv_path)

    # Steel CI - Calculate total energies from specific energies (kWh/kg)
    steel_data = params['steel']
    steel_total_virgin = steel_data['mass'] * steel_data['energy_virgin']
    steel_total_recycling = steel_data['mass'] * steel_data['energy_recycling']

    steel_ci = compute_ci_steel(
        mass=steel_data['mass'],
        recovery_rate=steel_data['recovery_rate'],
        energy_virgin=steel_data['energy_virgin'],
        energy_recycling=steel_data['energy_recycling']
    )

    # Aluminum CI - Calculate total energies from specific energies (kWh/kg)
    al_data = params['aluminum']
    al_total_virgin = al_data['mass'] * al_data['energy_virgin']
    al_total_recycling = al_data['mass'] * al_data['energy_recycling']

    aluminum_ci = compute_ci_aluminum(
        mass=al_data['mass'],
        recovery_rate=al_data['recovery_rate'],
        energy_virgin=al_data['energy_virgin'],
        energy_recycling=al_data['energy_recycling']
    )

    # Cell CI - Get materials data first
    materials_data = get_cell_materials_data_from_csv(csv_path)

    # Calculate total_recovered from materials: sum of (mass * recovery_rate)
    total_recovered = sum(mat['mass_kg'] * mat['recovery_rate'] for mat in materials_data)

    # Calculate total virgin energy for cell from materials: sum of (mass * energy_virgin)
    total_cell_energy_virgin = sum(mat['mass_kg'] * mat['energy_primary'] for mat in materials_data)

    # Calculate total recycling energy for cell: cell_mass * specific_energy (kWh/kg)
    cell_data = params['cell_total']
    total_cell_energy_recycling = cell_data['mass'] * cell_data['energy_recycling']

    # Cell CI - Method 1: Energy-based
    cell_ci_method1 = compute_ci_cell_method1(
        total_cell_mass=cell_data['mass'],
        total_energy_raw=total_cell_energy_virgin,
        total_energy_recycling=total_cell_energy_recycling,
        total_recovered=total_recovered
    )

    # Cell CI - Method 2: ADP-based
    cell_ci_method2 = compute_ci_cell_method2(
        total_cell_mass=cell_data['mass'],
        total_energy_recycling=total_cell_energy_recycling,
        total_recovered=total_recovered,
        total_adp=cell_data['adp_fossil']
    )

    # Cell CI - Method 3: Mass allocation
    cell_ci_method3 = compute_ci_cell_method3(materials_data, total_cell_energy_recycling)

    # Calculate combined/total CI values (weighted average)
    # Total mass = steel + aluminum + cell
    total_mass = steel_data['mass'] + al_data['mass'] + cell_data['mass']

    # Total CI using Method 1: Energy-based
    # Formula from Excel: =(G14*D6+N14*K6+Q4*U4)/302
    # Which is: (steel_ci * steel_mass + al_ci * al_mass + cell_ci * cell_mass) / total_mass
    total_ci_method1 = (
        steel_ci * steel_data['mass'] +
        aluminum_ci * al_data['mass'] +
        cell_ci_method1 * cell_data['mass']
    ) / total_mass

    # Total CI using Method 2: ADP-based
    total_ci_method2 = (
        steel_ci * steel_data['mass'] +
        aluminum_ci * al_data['mass'] +
        cell_ci_method2 * cell_data['mass']
    ) / total_mass

    # Total CI using Method 3: Mass allocation
    # Formula from Excel: =(G14*D6+N14*K6+Q11*W11+Q12*W12+Q13*W13+Q14*W14+Q15*W15+Q16*W16)/302
    # Which is: (steel_ci * steel_mass + al_ci * al_mass + sum(material_ci * material_mass)) / total_mass
    cell_materials_weighted_sum = sum(
        cell_ci_method3['ci_by_material'][mat['name']] * mat['mass_kg']
        for mat in materials_data
    )
    total_ci_method3 = (
        steel_ci * steel_data['mass'] +
        aluminum_ci * al_data['mass'] +
        cell_materials_weighted_sum
    ) / total_mass

    return {
        'steel_ci': steel_ci,
        'aluminum_ci': aluminum_ci,
        'cell_ci_method1': cell_ci_method1,
        'cell_ci_method2': cell_ci_method2,
        'cell_ci_method3': cell_ci_method3,
        'total_ci_method1': total_ci_method1,
        'total_ci_method2': total_ci_method2,
        'total_ci_method3': total_ci_method3,
        'parameters': params
    }


def print_ci_results(results):
    """
    Print formatted CI results.

    Parameters
    ----------
    results : dict
        Results dictionary from compute_all_ci_from_csv()
    """
    print("=" * 80)
    print("CIRCULARITY INDEX (CI) RESULTS")
    print("=" * 80)
    print()

    print("Individual Material CI:")
    print(f"  Steel CI:                    {results['steel_ci']:.6f}")
    print(f"  Aluminum CI:                 {results['aluminum_ci']:.6f}")
    print()

    print("Cell CI (3 Methods):")
    print(f"  Method 1 - Energy-based:     {results['cell_ci_method1']:.6f}")
    print(f"  Method 2 - ADP-based:        {results['cell_ci_method2']:.6f}")
    print(f"  Method 3 - Mass allocation:  {results['cell_ci_method3']['weighted_ci']:.6f}")
    print()

    print("Cell Materials CI (Method 3 - Mass Allocation):")
    for material, ci_value in results['cell_ci_method3']['ci_by_material'].items():
        print(f"  {material:15s} CI: {ci_value:.6f}")
    print()

    print("Total/Combined CI:")
    print(f"  Method 1 - Energy-based:     {results['total_ci_method1']:.6f}")
    print(f"  Method 2 - ADP-based:        {results['total_ci_method2']:.6f}")
    print(f"  Method 3 - Mass allocation:  {results['total_ci_method3']:.6f}")
    print()
    print("=" * 80)


def plot_ci_bar_chart(results, save_path='ci_bar_chart.png', dpi=300, figsize=(10, 6)):
    """
    Create journal-quality bar plot for CI indicators.
    Plots: Steel, Aluminum, Cell (Method 1), and Cumulative CI.

    Parameters
    ----------
    results : dict
        Results from compute_all_ci_from_csv()
    save_path : str
        Path to save figure
    dpi : int
        Resolution
    figsize : tuple
        Figure size (width, height)
    """
    # Set publication-quality style
    sns.set_style("whitegrid")
    sns.set_context("paper", font_scale=1.5)

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Prepare data
    categories = ['Steel', 'Aluminum', 'Cell', 'Cumulative']
    ci_values = [
        results['steel_ci'],
        results['aluminum_ci'],
        results['cell_ci_method1'],
        results['total_ci_method1']
    ]

    # Create color palette
    colors = sns.color_palette("viridis", len(categories))

    # Create bar plot
    bars = ax.bar(range(len(categories)), ci_values, color=colors,
                   edgecolor='black', linewidth=1.5, alpha=0.7)

    # Customize plot
    ax.set_xlabel('Component', fontweight='bold', fontsize=13)
    ax.set_ylabel('Circularity Index (CI)', fontweight='bold', fontsize=13)
    ax.set_title('Circularity Index by Component',
                 fontweight='bold', fontsize=16, pad=20)

    # Set x-axis labels
    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels(categories, rotation=0)

    # Add value labels on top of bars
    for bar, val in zip(bars, ci_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.4f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    # Add grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    # Set y-axis limits
    ax.set_ylim(0, max(ci_values) * 1.15)

    plt.tight_layout()
    plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
    print(f"\nCI bar chart saved to: {save_path}")
    plt.show()

    return fig, ax


def monte_carlo_ci(csv_path='ci_parameters.csv', n_samples=1000,
                   uncertainty_pct=0.05, confidence_level=0.95):
    """
    Perform Monte Carlo simulation for CI uncertainty analysis.

    Parameters
    ----------
    csv_path : str
        Path to parameters CSV
    n_samples : int
        Number of MC samples
    uncertainty_pct : float
        Uncertainty percentage (e.g., 0.05 = 5%)
    confidence_level : float
        Confidence level (e.g., 0.95 = 95%)

    Returns
    -------
    dict
        Statistics for each CI component
    """
    # Load base parameters
    base_params = load_parameters_from_csv(csv_path)

    # Storage for results
    mc_results = {
        'steel_ci': [],
        'aluminum_ci': [],
        'cell_ci': [],
        'cumulative_ci': []
    }

    # Monte Carlo sampling
    for _ in range(n_samples):
        # Perturb steel parameters
        steel_perturbed = {}
        for key, value in base_params['steel'].items():
            if value is not None and key in ['recovery_rate', 'energy_virgin', 'energy_recycling']:
                std_dev = abs(value * uncertainty_pct)
                perturbed = np.random.normal(value, std_dev)
                if key == 'recovery_rate':
                    perturbed = np.clip(perturbed, 0, 1)
                else:
                    perturbed = max(0.001, perturbed)
                steel_perturbed[key] = perturbed
            else:
                steel_perturbed[key] = value

        # Perturb aluminum parameters
        al_perturbed = {}
        for key, value in base_params['aluminum'].items():
            if value is not None and key in ['recovery_rate', 'energy_virgin', 'energy_recycling']:
                std_dev = abs(value * uncertainty_pct)
                perturbed = np.random.normal(value, std_dev)
                if key == 'recovery_rate':
                    perturbed = np.clip(perturbed, 0, 1)
                else:
                    perturbed = max(0.001, perturbed)
                al_perturbed[key] = perturbed
            else:
                al_perturbed[key] = value

        # Perturb cell materials
        materials_data = get_cell_materials_data_from_csv(csv_path)
        perturbed_materials = []
        for mat in materials_data:
            perturbed_mat = mat.copy()
            for key in ['recovery_rate', 'energy_primary']:
                if mat[key] is not None:
                    std_dev = abs(mat[key] * uncertainty_pct)
                    perturbed_val = np.random.normal(mat[key], std_dev)
                    if key == 'recovery_rate':
                        perturbed_val = np.clip(perturbed_val, 0, 1)
                    else:
                        perturbed_val = max(0.001, perturbed_val)
                    perturbed_mat[key] = perturbed_val
            perturbed_materials.append(perturbed_mat)

        # Perturb cell total recycling energy
        cell_data_perturbed = {}
        for key, value in base_params['cell_total'].items():
            if value is not None and key == 'energy_recycling':
                std_dev = abs(value * uncertainty_pct)
                perturbed = max(0.001, np.random.normal(value, std_dev))
                cell_data_perturbed[key] = perturbed
            else:
                cell_data_perturbed[key] = value

        # Compute CI values with perturbed parameters
        steel_ci = compute_ci_steel(
            mass=steel_perturbed['mass'],
            recovery_rate=steel_perturbed['recovery_rate'],
            energy_virgin=steel_perturbed['energy_virgin'],
            energy_recycling=steel_perturbed['energy_recycling']
        )

        al_ci = compute_ci_aluminum(
            mass=al_perturbed['mass'],
            recovery_rate=al_perturbed['recovery_rate'],
            energy_virgin=al_perturbed['energy_virgin'],
            energy_recycling=al_perturbed['energy_recycling']
        )

        # Calculate cell CI
        total_recovered = sum(mat['mass_kg'] * mat['recovery_rate'] for mat in perturbed_materials)
        total_cell_energy_virgin = sum(mat['mass_kg'] * mat['energy_primary'] for mat in perturbed_materials)
        total_cell_energy_recycling = cell_data_perturbed['mass'] * cell_data_perturbed['energy_recycling']

        cell_ci = compute_ci_cell_method1(
            total_cell_mass=cell_data_perturbed['mass'],
            total_energy_raw=total_cell_energy_virgin,
            total_energy_recycling=total_cell_energy_recycling,
            total_recovered=total_recovered
        )

        # Calculate cumulative CI
        total_mass = steel_perturbed['mass'] + al_perturbed['mass'] + cell_data_perturbed['mass']
        cumulative_ci = (
            steel_ci * steel_perturbed['mass'] +
            al_ci * al_perturbed['mass'] +
            cell_ci * cell_data_perturbed['mass']
        ) / total_mass

        # Store results
        mc_results['steel_ci'].append(steel_ci)
        mc_results['aluminum_ci'].append(al_ci)
        mc_results['cell_ci'].append(cell_ci)
        mc_results['cumulative_ci'].append(cumulative_ci)

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


def plot_ci_with_error_bars(csv_path='ci_parameters.csv', n_samples=1000,
                            uncertainty_pct=0.05, save_path='ci_with_error_bars.png',
                            dpi=600, figsize=(11, 9)):
    """
    Create CI bar plot with Monte Carlo error bars.

    Parameters
    ----------
    csv_path : str
        Path to parameters CSV
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
    stats, mc_results = monte_carlo_ci(csv_path, n_samples, uncertainty_pct)

    # Set style
    sns.set_style("whitegrid")
    sns.set_context("paper", font_scale=1.5)

    fig, ax = plt.subplots(figsize=figsize)

    # Prepare data
    categories = ['STL', 'Al', 'Cell', 'Final CI']
    keys = ['steel_ci', 'aluminum_ci', 'cell_ci', 'cumulative_ci']

    means = [stats[k]['mean'] for k in keys]
    errors_lower = [stats[k]['error_bar'][0] for k in keys]
    errors_upper = [stats[k]['error_bar'][1] for k in keys]

    # Create color palette
    colors = [
    "#d6604d",  # warm mid-red
    "#fddbc7",  # soft neutral (warm side)
    "#92c5de",  # light blue (cool side)
    "#2166ac"   # deep blue
        ]

    # Create bar plot with error bars
    x_pos = np.arange(len(categories))
    
    sep_x = x_pos[-2] + 0.5
    ax.axvline(
    sep_x,
    color='black',
    linestyle=(0, (4, 4)),
    linewidth=1.5,
    alpha=0.4
    )
    
    bars = ax.bar(x_pos, means, color=colors, edgecolor='black',
                   linewidth=1.5, alpha=1, width=0.4)
    ax.errorbar(x_pos, means, yerr=[errors_lower, errors_upper],
                fmt='none', ecolor='black', capsize=4, capthick=2, linewidth=2)

    for i, bar in enumerate(bars):
       height = bar.get_height()
       ax.text(
           bar.get_x() + bar.get_width() / 2,   # x position (center of bar)
           height + errors_upper[i] + 0.01,     # y position slightly above error bar
           f"{means[i]:.4f}",                   # formatted value (4 decimals)
           ha='center', va='bottom', fontsize=22, fontweight='bold'
           )


    # Customize plot
    #ax.set_xlabel('Component', fontsize=21)
    ax.set_ylabel('CI', fontsize=23, fontweight='bold')
    #ax.set_title(f'CI with 95% Confidence Intervals\n(Monte Carlo: {n_samples} samples, {uncertainty_pct*100}% uncertainty)',
     #            fontweight='bold', fontsize=14, pad=20)

    # Set x-axis labels
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories, rotation=0, fontweight='bold', fontsize=23)
    ax.tick_params(axis='y', labelsize=23)
    # Add grid
    ax.grid(False)
    ax.set_axisbelow(False)
    # Remove top and right border
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
    print(f"CI bar chart with error bars saved to: {save_path}")
    plt.show()

    # Print statistics
    print("\n" + "=" * 70)
    print("MONTE CARLO SIMULATION RESULTS")
    print("=" * 70)
    for cat, key in zip(categories, keys):
        s = stats[key]
        print(f"\n{cat}:")
        print(f"  Mean CI:     {s['mean']:.6f}")
        print(f"  Std Dev:     {s['std']:.6f}")
        print(f"  95% CI:      [{s['lower_ci']:.6f}, {s['upper_ci']:.6f}]")
    print("=" * 70)

    return fig, ax, stats


def tornado_plot_ci(component='cumulative', csv_path='ci_parameters.csv',
                    variation_pct=0.05, save_path='ci_tornado.png',
                    dpi=600, figsize=(12,8)):
    """
    Create tornado plot for CI sensitivity analysis.

    Parameters
    ----------
    component : str
        Component to analyze: 'steel', 'aluminum', 'cell', or 'cumulative'
    csv_path : str
        Path to parameters CSV
    variation_pct : float
        Percentage variation (±5%)
    save_path : str
        Path to save figure
    dpi : int
        Resolution
    figsize : tuple
        Figure size
    """
    # Load base parameters
    base_params = load_parameters_from_csv(csv_path)

    # Compute base CI
    base_results = compute_all_ci_from_csv(csv_path)

    if component == 'steel':
        base_ci = base_results['steel_ci']
        param_names = ['recovery_rate', 'energy_virgin', 'energy_recycling']
        material_key = 'steel'
    elif component == 'aluminum':
        base_ci = base_results['aluminum_ci']
        param_names = ['recovery_rate', 'energy_virgin', 'energy_recycling']
        material_key = 'aluminum'
    elif component == 'cell':
        base_ci = base_results['cell_ci_method1']
        # For cell, we'll vary the cell_total recycling energy and average recovery rate
        param_names = ['recovery_rate', 'energy_virgin', 'energy_recycling']
        material_key = 'cell_total'
    elif component == 'cumulative':
        base_ci = base_results['total_ci_method1']
        # For cumulative, vary all components
        param_names = ['recovery_rate', 'energy_virgin', 'energy_recycling']
        material_key = None
    else:
        raise ValueError(f"Unknown component: {component}")

    impacts = {}

    # Analyze parameters
    for param in param_names:
        if component in ['steel', 'aluminum']:
            base_val = base_params[material_key][param]

            # High variation
            test_params_high = base_params[material_key].copy()
            if base_val == 0 or abs(base_val) < 1e-10:
                test_params_high[param] = 0.01
            else:
                test_params_high[param] = base_val * (1 + variation_pct)

            if component == 'steel':
                ci_high = compute_ci_steel(**{k: test_params_high[k] for k in ['mass', 'recovery_rate', 'energy_virgin', 'energy_recycling']})
            else:
                ci_high = compute_ci_aluminum(**{k: test_params_high[k] for k in ['mass', 'recovery_rate', 'energy_virgin', 'energy_recycling']})

            # Low variation
            test_params_low = base_params[material_key].copy()
            if base_val == 0 or abs(base_val) < 1e-10:
                test_params_low[param] = 0.0
            else:
                test_params_low[param] = max(0, base_val * (1 - variation_pct))

            if component == 'steel':
                ci_low = compute_ci_steel(**{k: test_params_low[k] for k in ['mass', 'recovery_rate', 'energy_virgin', 'energy_recycling']})
            else:
                ci_low = compute_ci_aluminum(**{k: test_params_low[k] for k in ['mass', 'recovery_rate', 'energy_virgin', 'energy_recycling']})

        elif component == 'cell':
            # For cell, modify cell_total energy_recycling or material parameters
            if param == 'energy_recycling':
                base_val = base_params['cell_total']['energy_recycling']

                # High
                modified_params = base_params.copy()
                modified_params['cell_total'] = base_params['cell_total'].copy()
                modified_params['cell_total']['energy_recycling'] = base_val * (1 + variation_pct)

                materials_data = get_cell_materials_data_from_csv(csv_path)
                total_recovered = sum(mat['mass_kg'] * mat['recovery_rate'] for mat in materials_data)
                total_cell_energy_virgin = sum(mat['mass_kg'] * mat['energy_primary'] for mat in materials_data)
                total_cell_energy_recycling = modified_params['cell_total']['mass'] * modified_params['cell_total']['energy_recycling']
                ci_high = compute_ci_cell_method1(
                    modified_params['cell_total']['mass'],
                    total_cell_energy_virgin,
                    total_cell_energy_recycling,
                    total_recovered
                )

                # Low
                modified_params['cell_total']['energy_recycling'] = max(0.001, base_val * (1 - variation_pct))
                total_cell_energy_recycling = modified_params['cell_total']['mass'] * modified_params['cell_total']['energy_recycling']
                ci_low = compute_ci_cell_method1(
                    modified_params['cell_total']['mass'],
                    total_cell_energy_virgin,
                    total_cell_energy_recycling,
                    total_recovered
                )

            else:
                # For recovery_rate and energy_virgin, modify all cell materials
                materials_data = get_cell_materials_data_from_csv(csv_path)

                # High
                modified_materials = []
                for mat in materials_data:
                    mod_mat = mat.copy()
                    if param in ['recovery_rate', 'energy_primary']:
                        key = 'energy_primary' if param == 'energy_virgin' else param
                        base_val = mat[key]
                        if base_val:
                            mod_mat[key] = base_val * (1 + variation_pct) if key == 'energy_primary' else np.clip(base_val * (1 + variation_pct), 0, 1)
                    modified_materials.append(mod_mat)

                total_recovered = sum(mat['mass_kg'] * mat['recovery_rate'] for mat in modified_materials)
                total_cell_energy_virgin = sum(mat['mass_kg'] * mat['energy_primary'] for mat in modified_materials)
                total_cell_energy_recycling = base_params['cell_total']['mass'] * base_params['cell_total']['energy_recycling']
                ci_high = compute_ci_cell_method1(
                    base_params['cell_total']['mass'],
                    total_cell_energy_virgin,
                    total_cell_energy_recycling,
                    total_recovered
                )

                # Low
                modified_materials = []
                for mat in materials_data:
                    mod_mat = mat.copy()
                    if param in ['recovery_rate', 'energy_primary']:
                        key = 'energy_primary' if param == 'energy_virgin' else param
                        base_val = mat[key]
                        if base_val:
                            mod_mat[key] = max(0.001, base_val * (1 - variation_pct)) if key == 'energy_primary' else np.clip(base_val * (1 - variation_pct), 0, 1)
                    modified_materials.append(mod_mat)

                total_recovered = sum(mat['mass_kg'] * mat['recovery_rate'] for mat in modified_materials)
                total_cell_energy_virgin = sum(mat['mass_kg'] * mat['energy_primary'] for mat in modified_materials)
                ci_low = compute_ci_cell_method1(
                    base_params['cell_total']['mass'],
                    total_cell_energy_virgin,
                    total_cell_energy_recycling,
                    total_recovered
                )

        elif component == 'cumulative':
            # Vary all materials' parameters simultaneously
            # This is complex, so let's vary them proportionally
            # High: increase all
            results_high = compute_all_ci_from_csv(csv_path)  # Will compute with base
            # We need to modify and recompute, which is complex
            # Simplified: vary steel, al, and cell individually and see cumulative effect

            # Actually, let's create modified parameters
            modified_params = {}
            for mat_key in ['steel', 'aluminum', 'cell_total']:
                modified_params[mat_key] = base_params[mat_key].copy()
                if mat_key != 'cell_total' or param == 'energy_recycling':
                    if param in modified_params[mat_key] and modified_params[mat_key][param]:
                        base_val = modified_params[mat_key][param]
                        modified_params[mat_key][param] = base_val * (1 + variation_pct)

            # Also modify cell materials if needed
            materials_data = get_cell_materials_data_from_csv(csv_path)
            if param in ['recovery_rate', 'energy_virgin']:
                modified_materials_high = []
                for mat in materials_data:
                    mod_mat = mat.copy()
                    key = 'energy_primary' if param == 'energy_virgin' else param
                    if key in mat and mat[key]:
                        base_val = mat[key]
                        mod_mat[key] = base_val * (1 + variation_pct) if key == 'energy_primary' else np.clip(base_val * (1 + variation_pct), 0, 1)
                    modified_materials_high.append(mod_mat)
            else:
                modified_materials_high = materials_data

            # Compute CIs
            steel_ci_high = compute_ci_steel(**{k: modified_params['steel'][k] for k in ['mass', 'recovery_rate', 'energy_virgin', 'energy_recycling']})
            al_ci_high = compute_ci_aluminum(**{k: modified_params['aluminum'][k] for k in ['mass', 'recovery_rate', 'energy_virgin', 'energy_recycling']})

            total_recovered = sum(mat['mass_kg'] * mat['recovery_rate'] for mat in modified_materials_high)
            total_cell_energy_virgin = sum(mat['mass_kg'] * mat['energy_primary'] for mat in modified_materials_high)
            total_cell_energy_recycling = modified_params['cell_total']['mass'] * modified_params['cell_total']['energy_recycling']
            cell_ci_high = compute_ci_cell_method1(
                modified_params['cell_total']['mass'],
                total_cell_energy_virgin,
                total_cell_energy_recycling,
                total_recovered
            )

            total_mass = modified_params['steel']['mass'] + modified_params['aluminum']['mass'] + modified_params['cell_total']['mass']
            ci_high = (
                steel_ci_high * modified_params['steel']['mass'] +
                al_ci_high * modified_params['aluminum']['mass'] +
                cell_ci_high * modified_params['cell_total']['mass']
            ) / total_mass

            # Low variation
            modified_params = {}
            for mat_key in ['steel', 'aluminum', 'cell_total']:
                modified_params[mat_key] = base_params[mat_key].copy()
                if mat_key != 'cell_total' or param == 'energy_recycling':
                    if param in modified_params[mat_key] and modified_params[mat_key][param]:
                        base_val = modified_params[mat_key][param]
                        modified_params[mat_key][param] = max(0.001, base_val * (1 - variation_pct))

            if param in ['recovery_rate', 'energy_virgin']:
                modified_materials_low = []
                for mat in materials_data:
                    mod_mat = mat.copy()
                    key = 'energy_primary' if param == 'energy_virgin' else param
                    if key in mat and mat[key]:
                        base_val = mat[key]
                        mod_mat[key] = max(0.001, base_val * (1 - variation_pct)) if key == 'energy_primary' else np.clip(base_val * (1 - variation_pct), 0, 1)
                    modified_materials_low.append(mod_mat)
            else:
                modified_materials_low = materials_data

            steel_ci_low = compute_ci_steel(**{k: modified_params['steel'][k] for k in ['mass', 'recovery_rate', 'energy_virgin', 'energy_recycling']})
            al_ci_low = compute_ci_aluminum(**{k: modified_params['aluminum'][k] for k in ['mass', 'recovery_rate', 'energy_virgin', 'energy_recycling']})

            total_recovered = sum(mat['mass_kg'] * mat['recovery_rate'] for mat in modified_materials_low)
            total_cell_energy_virgin = sum(mat['mass_kg'] * mat['energy_primary'] for mat in modified_materials_low)
            total_cell_energy_recycling = modified_params['cell_total']['mass'] * modified_params['cell_total']['energy_recycling']
            cell_ci_low = compute_ci_cell_method1(
                modified_params['cell_total']['mass'],
                total_cell_energy_virgin,
                total_cell_energy_recycling,
                total_recovered
            )

            ci_low = (
                steel_ci_low * modified_params['steel']['mass'] +
                al_ci_low * modified_params['aluminum']['mass'] +
                cell_ci_low * modified_params['cell_total']['mass']
            ) / total_mass

        impacts[param] = {
            'base': base_ci,
            'low': ci_low,
            'high': ci_high,
            'impact_low': ci_low - base_ci,
            'impact_high': ci_high - base_ci,
            'range': abs(ci_high - ci_low)
        }

    # Sort by impact
    sorted_params = sorted(impacts.items(), key=lambda x: x[1]['range'], reverse=True)

    # Create tornado plot
    sns.set_style("whitegrid")
    sns.set_context("paper", font_scale=1.5)

    fig, ax = plt.subplots(figsize=figsize)
        
    # Prepare data
    label_map = {
    'energy_recycling': '$\\mathbf{E_{rec}}$',
    'energy_virgin': '$\\mathbf{E_{vir}}$',
    'recovery_rate': r'$\mathbf{Recovery}$' + '\n' + r'$\mathbf{Rate}$'
}

    param_labels = [label_map.get(p[0], p[0].replace('_', ' ').title()) for p in sorted_params]

    low_impacts = [p[1]['impact_low'] for p in sorted_params]
    high_impacts = [p[1]['impact_high'] for p in sorted_params]

    y_pos = np.arange(len(param_labels))

# Create horizontal bars
    bars_low = ax.barh(y_pos, low_impacts, height=0.4, align='center',
                   color='#9e9e9e', alpha=1, edgecolor='black', linewidth=0.9, label=f'-{variation_pct*100}%')
    bars_high = ax.barh(y_pos, high_impacts, height=0.4, align='center',
                    color='#4f81bd', alpha=1, edgecolor='black', linewidth=0.9, label=f'+{variation_pct*100}%')

# Add vertical line at base
    ax.axvline(x=0, color='black', linestyle='-', linewidth=1.5)

# Customize
    ax.set_yticks(y_pos)
    ax.set_yticklabels(param_labels, fontsize=22, rotation=0, ha='center')
    ax.set_xlabel('Change in CI', fontsize=23, fontweight='bold')

    ax.tick_params(axis='x', labelsize=22)
    ax.tick_params(axis='y', pad=22)

    # Compute a small horizontal offset so labels don't overlap the y-axis
    xmin, xmax = ax.get_xlim()
    offset = 0.01 * (xmax - xmin)   # 1% of axis width; tweak if needed

    # Add labels aligned near the center line, same x for all negatives/positives
    for i, (low, high) in enumerate(zip(low_impacts, high_impacts)):

    # Negative bar label (left side of zero)
        if abs(low) > 0.0001:
            ax.text(
            -offset, i, f'{low:.4f}',
            ha='right', va='center',
            fontsize=22, fontweight='bold',
            color='white'
        )

    # Positive bar label (right side of zero)
        if abs(high) > 0.0001:
            ax.text(
            offset, i, f'{high:.4f}',
            ha='left', va='center',
            fontsize=22, fontweight='bold',
            color='white'
        )

    # Add grid
    ax.grid(False)
    ax.set_axisbelow(False)
    
    # Legend
    ax.legend(loc='best', frameon=True, fontsize=22)
    # Remove top and right border
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
    print(f"\nTornado plot saved to: {save_path}")
    plt.show()

    # Print results
    print("\n" + "=" * 70)
    print(f"TORNADO ANALYSIS RESULTS - {component.upper()}")
    print("=" * 70)
    print(f"Base CI: {base_ci:.6f}")
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
    CI Analysis with visualization and uncertainty quantification.

    MONTE CARLO PARAMETERS:
    - Distribution: Normal (Gaussian)
    - Uncertainty: 5% std dev of parameter values
    - Samples: 1000
    - Confidence: 95%
    - Parameters varied: recovery_rate, energy_virgin, energy_recycling

    SENSITIVITY ANALYSIS PARAMETERS:
    - Variation: ±5% around base values
    - Parameters: recovery_rate, energy_virgin, energy_recycling
    """
    print("Loading parameters from ci_parameters.csv...")
    print()

    try:
        # Task 1: Compute and print CI results
        print("\n" + "="*70)
        print("TASK 1: COMPUTING AND PRINTING CI RESULTS")
        print("="*70)
        results = compute_all_ci_from_csv()
        print_ci_results(results)

        # Task 2: Create bar plot
        print("\n" + "="*70)
        print("TASK 2: CREATING BAR PLOT")
        print("="*70)
        plot_ci_bar_chart(results)

        # Task 3: Monte Carlo with error bars
        print("\n" + "="*70)
        print("TASK 3: MONTE CARLO SIMULATION WITH ERROR BARS")
        print("="*70)
        print("Monte Carlo Parameters:")
        print("  - Distribution: Normal (Gaussian)")
        print("  - Uncertainty: 5% std dev")
        print("  - Samples: 1000")
        print("  - Confidence: 95%")
        print("  - Parameters: recovery_rate, energy_virgin, energy_recycling")
        fig, ax, stats = plot_ci_with_error_bars(n_samples=1000, uncertainty_pct=0.05)

        # Task 4: Tornado plots for sensitivity analysis
        print("\n" + "="*70)
        print("TASK 4: TORNADO PLOTS (±5% VARIATION)")
        print("="*70)

        components = ['steel', 'aluminum', 'cell', 'cumulative']
        for component in components:
            save_path = f'ci_tornado_{component}.png'
            impacts, sorted_params = tornado_plot_ci(
                component=component,
                variation_pct=0.05,
                save_path=save_path
            )
            print("\n")

        print("\n" + "="*70)
        print("ALL TASKS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nGenerated files:")
        print("  - ci_bar_chart.png (basic bar plot)")
        print("  - ci_with_error_bars.png (Monte Carlo error bars)")
        print("  - ci_tornado_steel.png")
        print("  - ci_tornado_aluminum.png")
        print("  - ci_tornado_cell.png")
        print("  - ci_tornado_cumulative.png")
        print("="*70)

    except FileNotFoundError:
        print("Error: ci_parameters.csv not found in the script directory.")
        print("Please ensure the CSV file is in the same directory as this script.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()