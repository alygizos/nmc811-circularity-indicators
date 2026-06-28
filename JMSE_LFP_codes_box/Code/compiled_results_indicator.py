"""
Compiled Results Indicator Plot - LFP
Reads cumulative_results_indicators_lfp.csv and creates comparison bar plot
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'Arial'


def plot_compiled_indicators(csv_file='cumulative_results_indicators_lfp.csv',
                             save_path='compiled_indicators_comparison_lfp.png',
                             dpi=300,
                             figsize=(14, 7)):
    """
    Read cumulative results CSV and create comparison bar plot with error bars.

    Parameters:
    -----------
    csv_file : str
        Path to cumulative results CSV file
    save_path : str
        Path to save the output plot
    dpi : int
        Resolution of saved plot
    figsize : tuple
        Figure size (width, height)
    """

    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        print("Please make sure the LFP cumulative results file is named:")
        print("  cumulative_results_indicators_lfp.csv")
        return None, None

    # Read CSV
    df = pd.read_csv(csv_file)

    print("\n" + "=" * 70)
    print("COMPILED CIRCULARITY INDICATORS - LFP")
    print("=" * 70)

    # Extract data
    indicators = df['Indicator'].tolist()
    means = df['Mean'].tolist()
    ci_lowers = df['CI_Lower'].tolist()
    ci_uppers = df['CI_Upper'].tolist()

    # Calculate error bars
    errors_lower = [means[i] - ci_lowers[i] for i in range(len(means))]
    errors_upper = [ci_uppers[i] - means[i] for i in range(len(means))]

    # Print summary
    print("\nIndicator Summary:")
    print("-" * 70)

    for i, ind in enumerate(indicators):
        print(
            f"{ind:6s}: {means[i]:.4f}  "
            f"(95% CI: [{ci_lowers[i]:.4f}, {ci_uppers[i]:.4f}])"
        )

    print("=" * 70)

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Define colors for each indicator
    color_map = {
        'PCI': '#3498db',   # Blue
        'CI': '#2ecc71',    # Green
        'CEI': '#e74c3c',   # Red
        'ECPI': '#9b59b6',  # Purple
        'M': '#f39c12',     # Orange
        'R': '#1abc9c',     # Turquoise
        'E': '#e67e22'      # Dark Orange
    }

    colors = [color_map.get(ind, '#95a5a6') for ind in indicators]

    # Create bars
    x_pos = np.arange(len(indicators))

    bars = ax.bar(
        x_pos,
        means,
        color=colors,
        alpha=0.8,
        edgecolor='black',
        linewidth=1.5,
        width=0.6
    )

    # Add error bars
    ax.errorbar(
        x_pos,
        means,
        yerr=[errors_lower, errors_upper],
        fmt='none',
        ecolor='black',
        elinewidth=2.5,
        capsize=10,
        capthick=2.5,
        zorder=10
    )

    # Customize plot
    ax.set_xlabel('Circularity Indicator', fontsize=16, fontweight='bold')
    ax.set_ylabel('Indicator Value', fontsize=16, fontweight='bold')

    ax.set_title(
        'Comparison of LFP Circularity Indicators\n(with 95% Confidence Intervals)',
        fontsize=18,
        fontweight='bold',
        pad=20
    )

    # Set x-axis
    ax.set_xticks(x_pos)
    ax.set_xticklabels(indicators, fontsize=14, fontweight='bold')

    # Set y-axis based on upper CI, not only mean
    ax.set_ylim(0, max(ci_uppers) * 1.25)
    ax.tick_params(axis='y', labelsize=12)

    # Add value labels on bars
    for bar, mean_val, err_up in zip(bars, means, errors_upper):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            mean_val + err_up + max(ci_uppers) * 0.03,
            f'{mean_val:.4f}',
            ha='center',
            va='bottom',
            fontsize=13,
            fontweight='bold'
        )

    # Add grid
    ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.8)
    ax.xaxis.grid(False)
    ax.set_axisbelow(True)

    # Tight layout
    plt.tight_layout()

    # Save figure
    plt.savefig(save_path, dpi=dpi, bbox_inches='tight')

    print(f"\n{'=' * 70}")
    print(f"Comparison plot saved to: {save_path}")
    print(f"{'=' * 70}\n")

    return fig, ax


if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("LFP CIRCULARITY INDICATORS COMPILATION SCRIPT")
    print("=" * 70)

    # Folder where this script is located
    script_dir = Path(__file__).resolve().parent

    # Read the renamed LFP CSV from the same folder as this script
    csv_file = script_dir / "cumulative_results_indicators_lfp.csv"

    # Save the figure in the same folder as this script
    save_path = script_dir / "compiled_indicators_comparison_lfp.png"

    print("\nThis script reads cumulative results from:")
    print(f"  {csv_file}")
    print("\nand creates the LFP comparison bar plot with error bars.")
    print("=" * 70)

    fig, ax = plot_compiled_indicators(
        csv_file=str(csv_file),
        save_path=str(save_path),
        dpi=800,
        figsize=(14, 7)
    )

    if fig is not None:
        print("=" * 70)
        print("LFP COMPILATION COMPLETE!")
        print("=" * 70)
        print("\nFigure saved to:")
        print(f"  {save_path}")
        print("=" * 70)

        plt.show()