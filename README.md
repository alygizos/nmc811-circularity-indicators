# Circularity Indicator Assessment for NMC 811 Electric Vehicle Batteries

This repository contains Python scripts, processed input data, scenario definitions, uncertainty analysis outputs, and figure data supporting the manuscript:

"Assessing Circularity Indicators for Electric Vehicle Batteries: A Technical Comparison within a Life Cycle Context"

The study evaluates multiple circularity indicators, including PCI, CI, CEI, ECPI, and the M–R–E framework, for a representative NMC 811 electric vehicle battery system.

## Repository contents

- `data/`: Processed input data, scenario assumptions, and model outputs.
- `scripts/`: Python scripts used for indicator calculation, Monte Carlo uncertainty analysis, Sobol sensitivity analysis, and figure generation.
- `figures/`: Output figures used in the manuscript.
- `supplementary/`: Supplementary tables and extended results.

## Notes

Some life cycle inventory values were derived from external databases and models, including GREET, EverBatt, Ecoinvent, and literature sources. Original proprietary or licensed datasets are not redistributed in this repository.

## Requirements

The Python scripts require:

- Python 3.x
- pandas
- numpy
- matplotlib
- scipy
- SALib
- openpyxl

Install dependencies using:

```bash
pip install -r requirements.txt
