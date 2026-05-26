import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Global style
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'Arial'


def _prepare_sensitivity_data(excel_file, scenario_col, indicators):
    df = pd.read_excel(excel_file, sheet_name='Sheet1')
    scenarios = df[scenario_col].values

    data = {}
    for ind in indicators:
        means = df[f'{ind} Mean'].values
        try:
            ci_lower = df[f'{ind} CI Lower'].values
        except KeyError:
            ci_lower = df[f'{ind} CI lower'].values
        ci_upper = df[f'{ind} CI Upper'].values

        data[ind] = {
            'means': means,
            'errors_lower': means - ci_lower,
            'errors_upper': ci_upper - means
        }
    return scenarios, data


def _plot_panel(
    ax,
    scenarios,
    data,
    indicators,
    panel_title,
    bar_width=0.25,
    group_spacing=1.0,
    intra_group_gap=0.05,
    color_list=None,
    bar_alpha=0.85,
    edge_linewidth=1.1
):
    # Default colors
    if color_list is None:
        color_list = ['#f1b6da', '#e6f5d0', '#7fbc41']

    colors = {scenarios[i]: color_list[i % len(color_list)]
              for i in range(len(scenarios))}

    n_indicators = len(indicators)
    x_positions = np.arange(n_indicators) * group_spacing

    for i, scenario in enumerate(scenarios):
        offset = (i - (len(scenarios) - 1) / 2) * (bar_width + intra_group_gap)

        means = [data[ind]['means'][i] for ind in indicators]
        err_low = [data[ind]['errors_lower'][i] for ind in indicators]
        err_up = [data[ind]['errors_upper'][i] for ind in indicators]

        ax.bar(
            x_positions + offset, means, bar_width,
            color=colors[scenario], alpha=bar_alpha,
            edgecolor='black', linewidth=edge_linewidth
        )

#        ax.errorbar(
 #           x_positions + offset, means,
  #          yerr=[err_low, err_up],
   #         fmt='none', ecolor='black', elinewidth=1.2,
    #        capsize=3.5, capthick=1.2, zorder=10
     #   )

    ax.set_xticks(x_positions)
    ax.set_xticklabels(indicators, fontsize=24)
    ax.set_ylabel('Indicator Value', fontsize=24, fontweight='bold')
    ax.set_title(panel_title, fontsize=24, pad=8)
    ax.tick_params(axis='y', labelsize=24)
    
    
    # Remove top and right border
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add grid
    ax.grid(False)
    ax.set_axisbelow(False)

    return colors  # return colors to build global legend later


def plot_combined_sensitivity_figure(
    outfile='combined_sensitivity_panels.png',
    bar_width=0.2,
    group_spacing=1.0,
    intra_group_gap=0.05,
    color_list=None,
    bar_alpha=1,
    edge_linewidth=1.5
):
    """
    Create a 3-panel figure combining S1, S2, and S3 sensitivity studies,
    with consistent colors for worst / baseline / best scenarios.
    """

    # If no colors passed, use a fixed palette:
    # [Worst, Baseline, Best] = [dark red, light cream, dark blue]
    if color_list is None:
        color_list = ['#fee0b6', '#d8daeb', '#8073ac']

    studies = [
        {
            'excel': 'S1_sensitivity_study.xlsx',
            'scenario_col': 'CI Change (%)',
            'indicators': ['CI', 'E'],
            'panel_title': '(a) Scenario S1. Energy demand variation',
            # worst, baseline, best
            'scenario_order': [-20, 0, 20]
        },
        {
            'excel': 'S2_sensitivity_study.xlsx',
            'scenario_col': 'Change (%)',
            'indicators': ['PCI', 'CI', 'CEI', 'M'],
            'panel_title': '(b) Scenario 2. Recovery efficiency variation',
            # worst, baseline, best
            'scenario_order': [-5, 0, 5]
        },
        {
            'excel': 'S3_sensitivity_study.xlsx',
            'scenario_col': 'Collection Efficiency (%)',
            'indicators': ['PCI', 'ECPI', 'CEI', 'M', 'R', 'E'],
            'panel_title': '(c) Scenario 3. Collection efficiency variation',
            # worst, baseline, best
            'scenario_order': [70, 90, 100]
        }
    ]

    # ---------- load & reorder data, compute global max ----------
    processed = []
    global_max = 0.0

    for cfg in studies:
        scenarios_raw, data_raw = _prepare_sensitivity_data(
            cfg['excel'], cfg['scenario_col'], cfg['indicators']
        )

        # enforce [worst, baseline, best] scenario order
        order_vals = np.array(cfg['scenario_order'], dtype=float)
        scenarios_raw = scenarios_raw.astype(float)

        idx = [np.where(scenarios_raw == s)[0][0] for s in order_vals]
        scenarios = scenarios_raw[idx]

        # reorder each indicator’s arrays
        for ind in data_raw:
            for key in ['means', 'errors_lower', 'errors_upper']:
                arr = np.asarray(data_raw[ind][key], dtype=float)
                data_raw[ind][key] = arr[idx]

        processed.append((cfg, scenarios, data_raw))

        max_here = max([max(v['means']) for v in data_raw.values()])
        global_max = max(global_max, max_here)

    # ---------- create figure ----------
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharey=True)



    for ax, (cfg, scenarios, data) in zip(axes, processed):
        _plot_panel(
            ax,
            scenarios,
            data,
            cfg['indicators'],
            cfg['panel_title'],
            bar_width=bar_width,
            group_spacing=group_spacing,
            intra_group_gap=intra_group_gap,
            color_list=color_list,      # same colors for all panels
            bar_alpha=bar_alpha,
            edge_linewidth=edge_linewidth
        )

    # Shared x label
    axes[-1].set_xlabel('Circularity Indicators', fontsize=24, fontweight='bold')

    # Apply y limits
    for ax in axes:
        ax.set_ylim(0, global_max * 1.25)

    # ---------- single global legend (square patches with black border) ----------
    legend_labels = [
        "Worst-case scenario",
        "Baseline scenario",
        "Best-case scenario"
    ]

    handles = []
    for i in range(3):
        handles.append(
            plt.Line2D(
                [0], [0],
                marker='s',                  # square symbol
                markersize=24,               # size of square
                markerfacecolor=color_list[i],  # same colors as bars
                markeredgecolor='black',     # black border
                markeredgewidth=1.2,
                linestyle='none'             # no line
            )
        )

    fig.legend(
        handles,
        legend_labels,
        loc='lower center',
        ncol=3,
        frameon=False,
        fontsize=24,
        handletextpad=0.8,
        columnspacing=1.0,
        bbox_to_anchor=(0.5, -0.02)
    )

    fig.tight_layout(rect=[0, 0.05, 1, 0.95])
    fig.savefig(outfile, dpi=600, bbox_inches='tight')
    print(f'Combined sensitivity figure saved to: {outfile}')

    return fig, axes


# ----------------------------------------------------------------------
# Run directly
# ----------------------------------------------------------------------
if __name__ == "__main__":
    plot_combined_sensitivity_figure()
