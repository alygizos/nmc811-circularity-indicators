import pandas as pd
import os
from typing import Sequence
import math
import numpy as np

# Load data from CSV
def load_data_from_csv(csv_path='mre_indicator.csv'):
    """
    Load all material and general parameters from CSV file.
    Returns a dictionary with all parameters.
    """
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, csv_path)

    # Read the CSV file
    with open(full_path, 'r') as f:
        lines = f.readlines()

    # Find where material data ends (look for the Parameter section)
    material_end_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('Parameter,'):
            material_end_idx = i
            break

    # Read material data
    material_data = pd.read_csv(full_path, nrows=material_end_idx-1)
    material_data = material_data[material_data['Section'] == 'Material_Data']

    # Read general parameters (skip to Parameter section)
    params_data = pd.read_csv(full_path, skiprows=material_end_idx)

    # Create dictionary to store all parameters
    data = {}

    # Extract material arrays (7 materials: Li, Co, Ni, Cu, Mn, Al, Fe)
    data['materials'] = material_data['Material'].tolist()
    data['F'] = material_data['F'].tolist()
    data['fp'] = material_data['fp'].tolist()
    data['ft'] = material_data['ft'].tolist()
    data['m_i'] = material_data['m_i'].tolist()
    data['F_pyro'] = material_data['F_pyro'].tolist()
    data['eta_pyro'] = material_data['eta_pyro'].tolist()
    data['F_hydro'] = material_data['F_hydro'].tolist()
    data['eta_hydro'] = material_data['eta_hydro'].tolist()

    # Extract scalar parameters
    for _, row in params_data.iterrows():
        param_name = row['Parameter']
        value = row['Value']
        data[param_name] = value

    # Build arrays from numbered parameters
    data['SOF_retired'] = [data['SOF_retired_1'], data['SOF_retired_2'], data['SOF_retired_3']]
    data['Y_retired'] = [data['Y_retired_1'], data['Y_retired_2'], data['Y_retired_3']]
    data['m_repurpose'] = [data['m_repurpose_1'], data['m_repurpose_2'], data['m_repurpose_3']]
    data['qualitative_scores'] = [data['Q1'], data['Q2'], data['Q3'], data['Q4'], data['Q5'],
                                   data['Q6'], data['Q7'], data['Q8'], data['Q9']]
    data['F_rene'] = [data['F_rene_1'], data['F_rene_2'], data['F_rene_3'], data['F_rene_4']]
    data['E_rene'] = [data['E_rene_1'], data['E_rene_2'], data['E_rene_3'], data['E_rene_4']]
    data['E_total'] = [data['E_total_1'], data['E_total_2'], data['E_total_3'], data['E_total_4']]
    data['F_step'] = [data['F_step_1'], data['F_step_2'], data['F_step_3'], data['F_step_4']]
    data['ES_step'] = [data['ES_step_1'], data['ES_step_2'], data['ES_step_3'], data['ES_step_4']]
    data['E_used_j'] = [data['E_used_j_1'], data['E_used_j_2']]
    data['t_j'] = [data['t_j_1'], data['t_j_2']]
    data['F_j'] = [data['F_j_1'], data['F_j_2']]
    data['I_j'] = [data['I_j_1'], data['I_j_2']]
    # QP_ipf, QT_ipf, beta_i are already loaded as single values from params_data

    return data

# Route separation: hydro -> canonical names, solid -> *_solid (never clobbers hydro).
# MRE_CSV env var overrides the input path explicitly (handoff hook).
ROUTE = os.environ.get('LFP_ROUTE', 'hydro')
SUF   = '_solid' if ROUTE == 'solid' else ''

# Load all data from CSV
DATA = load_data_from_csv(os.environ.get('MRE_CSV', f'mre_indicator{SUF}.csv'))

# Material-specific arrays (7 materials: Lithium, Cobalt, Nickel, Copper, Manganese, Aluminum, Iron)
m_re = DATA['m_re_total']
m_vir = DATA['m_vir_total']

materials = DATA['materials']
F = DATA['F']
ft = DATA['ft']
fp = DATA['fp']

m_i = DATA['m_i']
F_pyro = DATA['F_pyro']          # All zeros (hydrometallurgical only)
eta_pyro = DATA['eta_pyro']      # All zeros (hydrometallurgical only)
F_hydro = DATA['F_hydro']
eta_hydro = DATA['eta_hydro']

m_c_i = DATA['m_c_i']
m_out_c_i = DATA['m_out_c_i']

C_trans = DATA['C_trans']
C_energy = DATA['C_energy']
C_labor = DATA['C_labor']
C_total = DATA['C_total']

# General parameters


wrr = DATA['wrr']
wte = DATA['wte']

m_residuals = DATA['m_residuals']
m_emissions = DATA['m_emissions']
m_landfill = DATA['m_landfill']
m_product_M7 = DATA['m_product_M7']
m_landfill_percent = DATA['m_landfill_percent']

n1 = DATA['n1']
n2 = DATA['n2']
n3 = DATA['n3']
n4 = DATA['n4']
n5 = DATA['n5']

# End of life indicators
m_waste = DATA['m_waste']
m_natural_resources = DATA['m_natural_resources']
m_product_R1 = DATA['m_product_R1']

m_remanufactured = DATA['m_remanufactured']
F_EV = DATA['F_EV']
F_generation = DATA['F_generation']
F_user = DATA['F_user']
F_mobile = DATA['F_mobile']
m_product_R2 = DATA['m_product_R2']
m_recycled_at_80 = DATA['m_recycled_at_80']

SOF_retired = DATA['SOF_retired_1'], DATA['SOF_retired_2'], DATA['SOF_retired_3']
Y_retired = DATA['Y_retired_1'], DATA['Y_retired_2'], DATA['Y_retired_3']
m_repurpose = DATA['m_repurpose_1'], DATA['m_repurpose_2'], DATA['m_repurpose_3']
m_product_R3 = DATA['m_product_R3']

recycled_fraction = DATA['recycled_fraction']
qualitative_scores = DATA['Q1'], DATA['Q2'], DATA['Q3'], DATA['Q4'], DATA['Q5'], DATA['Q6'], DATA['Q7'], DATA['Q8'], DATA['Q9']

r1 = DATA['r1']
r2 = DATA['r2']
r3 = DATA['r3']
r4 = DATA['r4']

# Energy indicators
F_rene = [DATA['F_rene_1'], DATA['F_rene_2'], DATA['F_rene_3'], DATA['F_rene_4']]  # Updated to use individual CSV inputs
E_rene = [DATA['E_rene_1'], DATA['E_rene_2'], DATA['E_rene_3'], DATA['E_rene_4']]  # Updated to use individual CSV inputs
E_total = DATA['E_total']

F_step = [DATA['F_step_1'], DATA['F_step_2'], DATA['F_step_3'], DATA['F_step_4']]
ES_step = [DATA['ES_step_1'], DATA['ES_step_2'], DATA['ES_step_3'], DATA['ES_step_4']]

E_extraction = DATA['E_extraction']
E_processing = DATA['E_processing']
E_assembly = DATA['E_assembly']
E_transport_manuf = DATA['E_transport_manuf']
E_collection = DATA['E_collection']
E_transport_recy = DATA['E_transport_recy']
E_pre_treatment = DATA['E_pre_treatment']
E_recovery = DATA['E_recovery']
E_repurpose = DATA['E_repurpose']
E_operational_secondlife = DATA['E_operational_secondlife']
f_saving_from_recycled = DATA['f_saving_from_recycled']
P_recycling = DATA['P_recycling']
P_secondlife = DATA['P_secondlife']
Y_retired_years = DATA['Y_retired_years']
service_life_primary_years = DATA['service_life_primary_years']

E_used_j = [DATA['E_used_j_1'], DATA['E_used_j_2']]
eta0 = DATA['eta0']
t_j = [DATA['t_j_1'], DATA['t_j_2']]
F_j = [DATA['F_j_1'], DATA['F_j_2']]
I_j = [DATA['I_j_1'], DATA['I_j_2']]
QP_ipf = [DATA['QP_ipf']]
QT_ipf = [DATA['QT_ipf']]
beta_i = [DATA['beta_i']]
alpha_pf_el = DATA['alpha_pf_el']
alpha_el_el = DATA['alpha_el_el']
alpha_pf_th = DATA['alpha_pf_th']
alpha_el_th = DATA['alpha_el_th']
alpha_pf_tr = DATA['alpha_pf_tr']
alpha_el_tr = DATA['alpha_el_tr']

e1= DATA['e1']
e2= DATA['e2']  
e3= DATA['e3']
e4= DATA['e4']

# Equations

def _safe_div(n, d):
    return float("nan") if d == 0 else n / d        # Prevents from dividing by zero

                                                                                                    # Material Indicators (M1–M7)

def M1(m_re: float, m_vir: float) -> float:                                                         # M1 Material Circularity Inflow
    
    """
    M1 = m_re / (m_re + m_vir)
    m_re: recycled material mass
    m_vir: virgin material mass
    """
    
    return _safe_div(m_re, m_re + m_vir)


def M2(F: Sequence[float], fp: Sequence[float] = None, ft: Sequence[float] = None) -> float:         # M2 Material Recovery Importance

    """
    M2 = sum_i F_i * (f_price_i + f_env_i)/2
    F_i: mass fraction of material i (sum = 1)
    f_p: price factor (P_i / P_m) --> provide P_i and P_m 
    Here we directly provide f_p and f_t
    f_p: economic importance factor for material i (0–1 or normalized)
    f_t: environmental impact factor for material i (0–1 or normalized)
    """
    if fp is None and ft is None:
        return float("nan")
    if fp is None:
        factors = list(map(float, ft))
    elif ft is None:
        factors = list(map(float, fp))
    else:
        factors = [(float(a)+float(b))/2.0 for a,b in zip(fp, ft)]
    return sum(f*fac for f,fac in zip(F, factors))

def M3(m_i: Sequence[float], F_pyro: Sequence[float], eta_pyro: Sequence[float],                    # M3 Product Material Recovery Potential
       F_hydro: Sequence[float], eta_hydro: Sequence[float]) -> float:
    
    """
    rec_i = F_pyro_i * eta_pyro_i + F_hydro_i * eta_hydro_i
    M3 = sum_i (m_i * rec_i)

    m_i       : mass of material i (kg)
    F_pyro_i  : share of pyrometallurgical route (0–1)
    F_hydro_i : share of hydrometallurgical route (0–1)
    eta_pyro_i, eta_hydro_i : recovery efficiencies of each route (0–1)

    Returns:
        Total recoverable mass (kg) --> can be normalized later if we devide with the total mass
    """
    
    rec = [fp * ep + fh * eh for fp, ep, fh, eh in zip(F_pyro, eta_pyro, F_hydro, eta_hydro)]
    return sum(mi/np.sum(m_i) * ri for mi, ri in zip(m_i, rec))


def M4(m_c_i: float, m_out_c_i: float) -> float:                                # M4 Regional material recovery cooperation

    """
    M4 = m_c,i / (m_c,i + m_out,c,i)
    m_c,i: mass recovered within region
    m_out,c,i: mass recovered outside region
    """

    in_region = float(m_c_i)
    out_region = float(m_out_c_i)
    return _safe_div(in_region, in_region + out_region)


def M5(m_c_i: float, m_out_ci: float,                                           # M5 Material recovery rates from cooperation in distance
       C_trans: float, C_energy: float,
       C_labor: float, C_total: float) -> float:

    """
    M5 = m_out,c,i * (1 - D_ci) / (m_c,i + m_out,c,i)
    where D_ci = (C_trans + C_energy + C_labor) / C_total

    m_c,i: mass recovered within region
    m_out,c,i: mass recovered outside region
    C_trans, C_energy, C_labor: cost components [$/kg]
    C_total: total cost per material [$/kg]
    """

    D_ci = _safe_div(float(C_trans) + float(C_energy) + float(C_labor), float(C_total))

    in_region = float(m_c_i)
    out_total = float(m_out_ci)
    effective_out = float(m_out_ci) * (1.0 - float(D_ci))
    return _safe_div(effective_out, in_region + out_total)


def M6(wrr: float, wte: float) -> float:                              # M6 Water circularity
    
    """
    WRR = V_r / V_t
    WTE = Vw_treated / Vw
    M6  = WRR * WTE
    V_r: recycled/reused water volume
    V_t: total water input
    Vw_treated: treated wastewater volume
    Vw: total wastewater volume
    """
    
    #WRR = _safe_div(V_r, V_t)
    #WTE = _safe_div(Vw_treated, Vw)
    #if math.isnan(WRR) or math.isnan(WTE):
    #    return float("nan")

    return wrr * wte


def M7(m_residuals: float, m_emissions: float, m_landfill: float, m_product: float, m_landfill_percent: float) -> float:       # M7 Weight of material outflow
    
    """
    M7 = 1 - (m_residuals + m_emissions + m_landfill) / m_product
    m_residuals: residual mass
    m_emissions: emitted mass-equivalent
    m_landfill: mass to landfill
    m_product: product/processed mass baseline
    """
    
    #return 1.0 - _safe_div(m_residuals + m_emissions + m_landfill, m_product)
    return 1-m_landfill_percent
                                                                                                    # End of life indicators

def R1_mass(m_waste: float, m_natural_resources: float, m_product_R1: float) -> float:                 # R1 Reduce
    
    """
    R1 = ((1 - m_waste) * (1 - m_natural_resources)) / m_product
    All inputs in kg
    """

    if m_product_R1 <= 0:
        return float("nan")
    val = ((1 - m_waste) * (1 - m_natural_resources)) / m_product_R1
    return max(0.0, min(1.0, val))


def R2(m_remanufactured: float,                                                                     # R2 Remanufacturing
       F_EV: float,
       F_generation: float,
       F_user: float,
       F_mobile: float,
       m_product: float,
       m_recycled_at_80: float) -> float:
    
    """
R2 = [ m_remanufactured * (F_EV + F_generation + F_user + F_mobile) ] 
         / [ m_product - m_recycled_at_80 ]

    m_remanufactured : mass of remanufactured batteries (kg/year)
    F_EV             : fraction of remanufactured batteries returned to EV use
    F_generation     : fraction used for generation-side energy storage
    F_user           : fraction used for user-side energy storage
    F_mobile         : fraction used for mobile power supply
    m_product        : total product mass baseline (kg/year)
    m_recycled_at_80 : mass of batteries recycled when SOH < 80% (kg/year)
    """
    
    numerator = m_remanufactured * (F_EV + F_generation + F_user + F_mobile)
    denominator = m_product - m_recycled_at_80
    return _safe_div(numerator, denominator)


def R3(                                                                                             # R3 Repurposing-Echelon Utilization 
    SOF_retired: Sequence[float],
    Y_retired: Sequence[float],
    m_repurpose: Sequence[float],
    m_product: float,
    SOH_threshold: float = 0.8,
    Y_ref: float = 5.0,
) -> float:
    
    """
    Repurposing–Echelon Utilization (R3)

    x = sum_i [ (1 - SOF_retired_i)/(1 - SOH_threshold)
                * (Y_retired_i / Y_ref)
                * (m_repurpose_i / m_product) ]
    R3 = 1 - exp(-x)

    SOF_retired_i: state-of-function at retirement from secondary use (0–1)
    Y_retired_i  : years in secondary use
    m_repurpose_i: repurposed mass in pathway i (kg/yr)
    m_product    : product mass baseline (kg/yr)
    """
    
    if m_product <= 0 or Y_ref <= 0:
        return float("nan")
    if len(SOF_retired) != len(Y_retired) or len(SOF_retired) != len(m_repurpose):
        raise ValueError("Input sequences must have equal length.")

    denom_soh = 1.0 - float(SOH_threshold)
    if denom_soh <= 0:
        return float("nan")

    x = 0.0
    for sof, y, mrep in zip(SOF_retired, Y_retired, m_repurpose):
        term = ((1.0 - float(sof)) / denom_soh) * _safe_div(float(y), float(Y_ref)) \
               * _safe_div(float(mrep), float(m_product))
       
        if not math.isnan(term) and term > 0:
            x += term

    r3 = 1.0 - math.exp(-x)
    return max(0.0, min(1.0, r3))


def R4(recycled_fraction: float, qualitative_scores: Sequence[float]) -> float:                         # R4 Recycling
    
    """
    R4 = recycled_fraction * mean(Q_i)
    recycled_fraction: share (0–1) of product recycled
    Q_i: qualitative scores (0–1) from a standardized checklist/survey
    """
    
    Q = list(map(float, qualitative_scores))
    if len(Q) == 0:
        return float("nan")
    return max(0.0, min(1.0, float(recycled_fraction) * (sum(Q)/len(Q))))

                                                                                                        # Energy indicators
                                                                                                                                         
def E1(F_rene: Sequence[float], E_rene: Sequence[float]) -> float:  # E1 Share of renewable energy
    """
    E1 = Σ_i (F_rene_i * E_rene_i)
    """
    if len(F_rene) != len(E_rene):
        raise ValueError("F_rene and E_rene must have the same length.")
    return sum(f * e for f, e in zip(F_rene, E_rene))  # Updated to sum products of F_rene and E_rene


def E2(F_step: Sequence[float], ES_step: Sequence[float]) -> float:                                      # E2 Energy efficiency 

    """
    ESF = sum_i F_step_i * 1/(1 + ES_step_i)
    E2  = ESF / (1 + ESF)
    F_step_i: step weight or energy share
    ES_step_i: energy-saving factor (≥0) vs baseline
    """
    
    ESF = sum(float(f) * (1.0/(1.0 + float(es))) for f,es in zip(F_step, ES_step))
    return _safe_div(ESF, 1.0 + ESF)


def E3(E_extraction: float, E_processing: float, E_assembly: float, E_transport_manuf: float,            # E3 Energy consumption in recycling and end-of-life
       E_collection: float, E_transport_recy: float, E_pre_treatment: float, E_recovery: float,
       E_repurpose: float, E_operational_secondlife: float, f_saving_from_recycled: float,
       P_recycling: float, P_secondlife: float, Y_retired_years: float, service_life_primary_years: float = 8.0) -> float:
    
    """
    E_manuf = E_extraction + E_processing + E_assembly + E_transport_manuf
    E_recy  = E_collection + E_transport_recy + E_pre_treatment + E_recovery
    E_second= E_repurpose + E_operational_secondlife
    E_net   = E_manuf - [ f_saving_from_recycled*P_recycling*E_recy
                          + P_secondlife*E_second*(Y_retired_years/service_life_primary_years) ]
    E3      = E_net / E_manuf
    """
    
    E_manuf = float(E_extraction + E_processing + E_assembly + E_transport_manuf)
    E_recy  = float(E_collection + E_transport_recy + E_pre_treatment + E_recovery)
    E_second= float(E_repurpose + E_operational_secondlife)
    term_recy = float(f_saving_from_recycled) * float(P_recycling) * E_recy
    term_second = float(P_secondlife) * E_second * _safe_div(float(Y_retired_years), float(service_life_primary_years))
    E_net = E_manuf - (term_recy + term_second)
    return _safe_div(E_net, E_manuf)


def E4(E_used_j: Sequence[float], eta0: float, t_j: Sequence[float], F_j: Sequence[float], I_j: Sequence[float],                    # E4 Energy return indicator in battery lifecycle
       QP_ipf: Sequence[float], QT_ipf: Sequence[float], beta_i: Sequence[float],
       alpha_pf_el: float, alpha_el_el: float, alpha_pf_th: float, alpha_el_th: float,
       alpha_pf_tr: float, alpha_el_tr: float) -> float:
    """
    ER = [Σ_j (E_used_j/η0 * t_j * F_j * I_j)] /
         {Σ_i QP_ipf_i [β_i*(α_pf_el/α_el_el) + (1-β_i)*(α_pf_th/α_el_th)]
          + Σ_i QT_ipf_i *(α_pf_tr/α_el_tr)}
    E4 = 1 - 1/(ER + 1)
    """
    numerator = sum((float(Eu)/float(eta0)) * float(t) * float(F) * float(I)
                    for Eu, t, F, I in zip(E_used_j, t_j, F_j, I_j))

    el_ratio = float(alpha_pf_el) / float(alpha_el_el)
    th_ratio = float(alpha_pf_th) / float(alpha_el_th)
    tr_ratio = float(alpha_pf_tr) / float(alpha_el_tr)

    denom_prod = sum(float(Qp) * (float(b) * el_ratio + (1.0 - float(b)) * th_ratio)
                     for Qp, b in zip(QP_ipf, beta_i))
    denom_trans = sum(float(Qt) * tr_ratio for Qt in QT_ipf)

    ER = (numerator) / (denom_prod + denom_trans) if (denom_prod + denom_trans) else float("nan")
    
    return 1.0 - 1.0 / (ER + 1.0)


def total_M(M1: float, M2: float, M3: float, M4: float, M5: float, M6: float, M7: float,n1: float,n2: float,n3: float,n4: float,n5: float) -> float:
    """
    Total Material Indicator
    """
    return n1 * M1 + n2 * M2 * M3 + n3 * (M4 + M5) + n4 * M6 + n5 * M7

def total_R(R1: float, R2: float, R3: float, R4: float,r1: float,r2: float,r3: float,r4: float) -> float:
    """
    Total Recovery Indicator
    total_R = (R1 + R2 + R3 + R4) / 4
    """
    return r1 * R1 + r2 * R2 + r3 * R3 + r4 * R4

def total_E(E1: float, E2: float, E3: float, E4: float,e1: float,e2: float,e3: float,e4: float) -> float:
    """
    Total Energy Indicator
    """
    return e1 * E1 + e2 * E2 + e3 * E3 + e4 * E4


M1_value = M1(m_re, m_vir)
M2_value = M2(F, fp, ft)
M3_value = M3(m_i, F_pyro, eta_pyro, F_hydro, eta_hydro)
M4_value = M4(m_c_i, m_out_c_i)
M5_value = M5(m_c_i, m_out_c_i, C_trans, C_energy, C_labor, C_total)
M6_value = M6(wrr, wte)
M7_value = M7(m_residuals, m_emissions, m_landfill, m_product_M7, m_landfill_percent)

total_M_value = total_M(M1_value, M2_value, M3_value, M4_value, M5_value, M6_value, M7_value,n1,n2,n3,n4,n5)

R1_value = R1_mass(m_waste, m_natural_resources, m_product_R1)  
R2_value = R2(m_remanufactured, F_EV, F_generation, F_user, F_mobile, m_product_R2, m_recycled_at_80)
R3_value = R3(SOF_retired, Y_retired, m_repurpose, m_product_R3)
R4_value = R4(recycled_fraction, qualitative_scores)
total_R_value = total_R(R1_value, R2_value, R3_value, R4_value,r1,r2,r3,r4)

E1_value = E1(F_rene, E_rene)
E2_value = E2(F_step, ES_step)
E3_value = E3(E_extraction, E_processing, E_assembly, E_transport_manuf,
               E_collection, E_transport_recy, E_pre_treatment, E_recovery,
               E_repurpose, E_operational_secondlife, f_saving_from_recycled,
               P_recycling, P_secondlife, Y_retired_years, service_life_primary_years)
E4_value = E4(E_used_j, eta0, t_j, F_j, I_j, QP_ipf, QT_ipf, beta_i,
               alpha_pf_el, alpha_el_el, alpha_pf_th, alpha_el_th,
               alpha_pf_tr, alpha_el_tr)
total_E_value = total_E(E1_value, E2_value, E3_value, E4_value,e1,e2,e3,e4)


# Monte Carlo simulation for uncertainty analysis
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from SALib.sample import saltelli
from SALib.analyze import sobol


def monte_carlo_mre(n_samples=1000, uncertainty_pct=0.05, confidence_level=0.95):
    """
    Perform Monte Carlo simulation to estimate uncertainty in MRE indicators.
    Perturbs ALL relevant parameters similar to PCI approach.

    Args:
        n_samples: Number of Monte Carlo samples
        uncertainty_pct: Uncertainty as a fraction of the mean (e.g., 0.05 = 5%)
        confidence_level: Confidence level for error bars (e.g., 0.95 = 95%)

    Returns:
        Dictionary containing mean values, standard deviation, and confidence intervals
    """
    # Storage for results
    mc_results = {
        'M1': [], 'M2': [], 'M3': [], 'M4': [], 'M5': [], 'M6': [], 'M7': [],
        'total_M': [],
        'R1': [], 'R2': [], 'R3': [], 'R4': [],
        'total_R': [],
        'E1': [], 'E2': [], 'E3': [], 'E4': [],
        'total_E': []
    }

    # Monte Carlo sampling with perturbation of all relevant parameters
    for _ in range(n_samples):
        # Perturb Material indicator parameters
        m_re_sim = max(0.001, np.random.normal(m_re, abs(m_re * uncertainty_pct)))
        m_vir_sim = max(0.001, np.random.normal(m_vir, abs(m_vir * uncertainty_pct)))

        # Perturb material arrays
        m_i_sim = [max(0.001, np.random.normal(mi, abs(mi * uncertainty_pct))) for mi in m_i]
        eta_hydro_sim = [np.clip(np.random.normal(eta, abs(eta * uncertainty_pct)), 0, 1) for eta in eta_hydro]

        # Perturb scalar parameters for M indicators
        m_c_i_sim = max(0.001, np.random.normal(m_c_i, abs(m_c_i * uncertainty_pct)))
        m_out_c_i_sim = max(0.001, np.random.normal(m_out_c_i, abs(m_out_c_i * uncertainty_pct)))
        C_trans_sim = max(0.001, np.random.normal(C_trans, abs(C_trans * uncertainty_pct)))
        C_energy_sim = max(0.001, np.random.normal(C_energy, abs(C_energy * uncertainty_pct)))
        C_labor_sim = max(0.001, np.random.normal(C_labor, abs(C_labor * uncertainty_pct)))
        C_total_sim = max(0.001, np.random.normal(C_total, abs(C_total * uncertainty_pct)))
        wrr_sim = np.clip(np.random.normal(wrr, abs(wrr * uncertainty_pct)), 0, 1)
        wte_sim = np.clip(np.random.normal(wte, abs(wte * uncertainty_pct)), 0, 1)

        # Perturb R indicator parameters
        m_waste_sim = max(0, np.random.normal(m_waste, abs(m_waste * uncertainty_pct)))
        m_natural_resources_sim = max(0, np.random.normal(m_natural_resources, abs(m_natural_resources * uncertainty_pct)))
        m_product_R1_sim = max(0.001, np.random.normal(m_product_R1, abs(m_product_R1 * uncertainty_pct)))
        m_remanufactured_sim = max(0, np.random.normal(m_remanufactured, abs(m_remanufactured * uncertainty_pct)))
        m_product_R2_sim = max(0.001, np.random.normal(m_product_R2, abs(m_product_R2 * uncertainty_pct)))
        m_recycled_at_80_sim = max(0, np.random.normal(m_recycled_at_80, abs(m_recycled_at_80 * uncertainty_pct)))
        recycled_fraction_sim = np.clip(np.random.normal(recycled_fraction, abs(recycled_fraction * uncertainty_pct)), 0, 1)

        # Perturb E indicator parameters
        E_extraction_sim = max(0, np.random.normal(E_extraction, abs(E_extraction * uncertainty_pct) if E_extraction > 0 else 0.01))
        E_processing_sim = max(0.001, np.random.normal(E_processing, abs(E_processing * uncertainty_pct)))
        E_assembly_sim = max(0.001, np.random.normal(E_assembly, abs(E_assembly * uncertainty_pct)))
        E_transport_manuf_sim = max(0, np.random.normal(E_transport_manuf, abs(E_transport_manuf * uncertainty_pct)))
        E_collection_sim = max(0, np.random.normal(E_collection, abs(E_collection * uncertainty_pct) if E_collection > 0 else 0.01))
        E_transport_recy_sim = max(0, np.random.normal(E_transport_recy, abs(E_transport_recy * uncertainty_pct)))
        E_pre_treatment_sim = max(0.001, np.random.normal(E_pre_treatment, abs(E_pre_treatment * uncertainty_pct)))
        E_recovery_sim = max(0.001, np.random.normal(E_recovery, abs(E_recovery * uncertainty_pct)))

        # Compute M indicators with perturbed parameters
        M1_sim = M1(m_re_sim, m_vir_sim)
        M2_sim = M2(F, fp, ft)  # Uses fixed material fractions
        M3_sim = M3(m_i_sim, F_pyro, eta_pyro, F_hydro, eta_hydro_sim)
        M4_sim = M4(m_c_i_sim, m_out_c_i_sim)
        M5_sim = M5(m_c_i_sim, m_out_c_i_sim, C_trans_sim, C_energy_sim, C_labor_sim, C_total_sim)
        M6_sim = M6(wrr_sim, wte_sim)
        M7_sim = M7(m_residuals, m_emissions, m_landfill, m_product_M7, m_landfill_percent)

        total_M_sim = total_M(M1_sim, M2_sim, M3_sim, M4_sim, M5_sim, M6_sim, M7_sim, n1, n2, n3, n4, n5)

        # Compute R indicators with perturbed parameters
        R1_sim = R1_mass(m_waste_sim, m_natural_resources_sim, m_product_R1_sim)
        R2_sim = R2(m_remanufactured_sim, F_EV, F_generation, F_user, F_mobile, m_product_R2_sim, m_recycled_at_80_sim)
        R3_sim = R3(SOF_retired, Y_retired, m_repurpose, m_product_R3)  # Using fixed values
        R4_sim = R4(recycled_fraction_sim, qualitative_scores)

        total_R_sim = total_R(R1_sim, R2_sim, R3_sim, R4_sim, r1, r2, r3, r4)

        # Compute E indicators with perturbed parameters
        E1_sim = E1(F_rene, E_rene)  # Using fixed renewable fractions
        E2_sim = E2(F_step, ES_step)  # Using fixed efficiency factors
        E3_sim = E3(E_extraction_sim, E_processing_sim, E_assembly_sim, E_transport_manuf_sim,
                    E_collection_sim, E_transport_recy_sim, E_pre_treatment_sim, E_recovery_sim,
                    E_repurpose, E_operational_secondlife, f_saving_from_recycled,
                    P_recycling, P_secondlife, Y_retired_years, service_life_primary_years)
        E4_sim = E4(E_used_j, eta0, t_j, F_j, I_j, QP_ipf, QT_ipf, beta_i,
                    alpha_pf_el, alpha_el_el, alpha_pf_th, alpha_el_th, alpha_pf_tr, alpha_el_tr)

        total_E_sim = total_E(E1_sim, E2_sim, E3_sim, E4_sim, e1, e2, e3, e4)

        # Store results
        mc_results['M1'].append(M1_sim)
        mc_results['M2'].append(M2_sim)
        mc_results['M3'].append(M3_sim)
        mc_results['M4'].append(M4_sim)
        mc_results['M5'].append(M5_sim)
        mc_results['M6'].append(M6_sim)
        mc_results['M7'].append(M7_sim)
        mc_results['total_M'].append(total_M_sim)

        mc_results['R1'].append(R1_sim)
        mc_results['R2'].append(R2_sim)
        mc_results['R3'].append(R3_sim)
        mc_results['R4'].append(R4_sim)
        mc_results['total_R'].append(total_R_sim)

        mc_results['E1'].append(E1_sim)
        mc_results['E2'].append(E2_sim)
        mc_results['E3'].append(E3_sim)
        mc_results['E4'].append(E4_sim)
        mc_results['total_E'].append(total_E_sim)

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
            'error_bar': (abs(mean_val - lower_ci), abs(upper_ci - mean_val))
        }

    return stats, mc_results


def plot_mre_with_error_bars(n_samples=1000, uncertainty_pct=0.05,
                             save_path='mre_with_error_bars.png', dpi=300, figsize=(12, 6)):
    """
    Create bar plot with Monte Carlo error bars for total_M, total_R, and total_E.

    Args:
        n_samples: Number of Monte Carlo samples
        uncertainty_pct: Uncertainty as a fraction of the mean
        save_path: Path to save the figure
        dpi: Resolution for saved figure
        figsize: Figure size
    """
    print(f"\nRunning Monte Carlo simulation with {n_samples} samples...")
    stats, mc_results = monte_carlo_mre(n_samples, uncertainty_pct)

    # Set publication-quality style
    sns.set_style("whitegrid")
    sns.set_context("paper", font_scale=1.5)

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Prepare data for the three total indicators
    indicators = ['total_M', 'total_R', 'total_E']
    labels = ['Total M\n(Material)', 'Total R\n(Recovery)', 'Total E\n(Energy)']
    means = [stats[ind]['mean'] for ind in indicators]
    errors_lower = [stats[ind]['error_bar'][0] for ind in indicators]
    errors_upper = [stats[ind]['error_bar'][1] for ind in indicators]

    # Create color palette
    colors = ['#3498db', '#e74c3c', '#2ecc71']

    # Create bar plot with error bars
    x_pos = np.arange(len(indicators))
    bars = ax.bar(x_pos, means, color=colors, edgecolor='black',
                   linewidth=1.2, alpha=0.8)
    ax.errorbar(x_pos, means, yerr=[errors_lower, errors_upper],
                fmt='none', ecolor='black', capsize=5, capthick=2, linewidth=2)

    # Add value labels on top of bars
    for i, (bar, val) in enumerate(zip(bars, means)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.4f}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    # Customize plot
    ax.set_xlabel('Indicator', fontweight='bold', fontsize=14)
    ax.set_ylabel('Indicator Value', fontweight='bold', fontsize=14)
    ax.set_title(f'MRE Indicators with 95% Confidence Intervals\n(Monte Carlo: {n_samples} samples, {uncertainty_pct*100}% uncertainty)',
                 fontweight='bold', fontsize=14, pad=20)

    # Set x-axis labels
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=12)

    # Add grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    # Adjust layout
    plt.tight_layout()

    # Save figure in the mre directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_save_path = os.path.join(script_dir, save_path)
    plt.savefig(full_save_path, dpi=dpi, bbox_inches='tight')
    print(f"Bar chart with error bars saved to: {full_save_path}")

    # plt.show()  # Disabled for non-interactive runs
    plt.close()

    # Print statistics for totals
    print("\n" + "=" * 70)
    print("MONTE CARLO SIMULATION RESULTS - TOTAL INDICATORS")
    print("=" * 70)
    for ind, label in zip(indicators, labels):
        print(f"\n{label.replace(chr(10), ' ')}:")
        s = stats[ind]
        print(f"  Mean:        {s['mean']:.6f}")
        print(f"  Std Dev:     {s['std']:.6f}")
        print(f"  95% CI:      [{s['lower_ci']:.6f}, {s['upper_ci']:.6f}]")

    # Print statistics for individual M indicators
    print("\n" + "=" * 70)
    print("INDIVIDUAL MATERIAL INDICATORS (M)")
    print("=" * 70)
    m_indicators = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7']
    m_labels = [
        'M1 (Material Circularity Inflow)',
        'M2 (Material Recovery Importance)',
        'M3 (Product Material Recovery Potential)',
        'M4 (Regional Material Recovery Cooperation)',
        'M5 (Material Recovery Rates from Distance)',
        'M6 (Water Circularity)',
        'M7 (Weight of Material Outflow)'
    ]
    for ind, label in zip(m_indicators, m_labels):
        s = stats[ind]
        print(f"\n{label}:")
        print(f"  Mean:        {s['mean']:.6f}")
        print(f"  Std Dev:     {s['std']:.6f}")
        print(f"  95% CI:      [{s['lower_ci']:.6f}, {s['upper_ci']:.6f}]")

    # Print statistics for individual R indicators
    print("\n" + "=" * 70)
    print("INDIVIDUAL RECOVERY INDICATORS (R)")
    print("=" * 70)
    r_indicators = ['R1', 'R2', 'R3', 'R4']
    r_labels = [
        'R1 (Reduce)',
        'R2 (Remanufacturing)',
        'R3 (Repurposing-Echelon Utilization)',
        'R4 (Recycling)'
    ]
    for ind, label in zip(r_indicators, r_labels):
        s = stats[ind]
        print(f"\n{label}:")
        print(f"  Mean:        {s['mean']:.6f}")
        print(f"  Std Dev:     {s['std']:.6f}")
        print(f"  95% CI:      [{s['lower_ci']:.6f}, {s['upper_ci']:.6f}]")

    # Print statistics for individual E indicators
    print("\n" + "=" * 70)
    print("INDIVIDUAL ENERGY INDICATORS (E)")
    print("=" * 70)
    e_indicators = ['E1', 'E2', 'E3', 'E4']
    e_labels = [
        'E1 (Share of Renewable Energy)',
        'E2 (Energy Efficiency)',
        'E3 (Energy Consumption in Recycling/EOL)',
        'E4 (Energy Return Indicator)'
    ]
    for ind, label in zip(e_indicators, e_labels):
        s = stats[ind]
        print(f"\n{label}:")
        print(f"  Mean:        {s['mean']:.6f}")
        print(f"  Std Dev:     {s['std']:.6f}")
        print(f"  95% CI:      [{s['lower_ci']:.6f}, {s['upper_ci']:.6f}]")

    print("=" * 70)

    return fig, ax, stats


def plot_individual_indicators(stats, save_dir='', dpi=300, figsize=(14, 5), suffix=''):
    """
    Create separate bar plots for individual M, R, and E indicators with error bars.

    Args:
        stats: Dictionary containing statistics from Monte Carlo simulation
        save_dir: Directory to save the figures
        dpi: Resolution for saved figures
        figsize: Figure size (width, height) in inches
    """
    # Set publication-quality style
    sns.set_style("whitegrid")
    sns.set_context("paper", font_scale=1.3)

    # Get script directory for saving
    if not save_dir:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        save_dir = script_dir

    # ========== PLOT M INDICATORS ==========
    m_indicators = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7']
    m_labels = ['M1\n(Circularity\nInflow)', 'M2\n(Recovery\nImportance)',
                'M3\n(Recovery\nPotential)', 'M4\n(Regional\nCooperation)',
                'M5\n(Distance\nRates)', 'M6\n(Water\nCircularity)',
                'M7\n(Outflow\nWeight)']

    fig_m, ax_m = plt.subplots(figsize=figsize)

    means_m = [stats[ind]['mean'] for ind in m_indicators]
    errors_lower_m = [stats[ind]['error_bar'][0] for ind in m_indicators]
    errors_upper_m = [stats[ind]['error_bar'][1] for ind in m_indicators]

    colors_m = sns.color_palette("viridis", len(m_indicators))
    x_pos_m = np.arange(len(m_indicators))

    bars_m = ax_m.bar(x_pos_m, means_m, color=colors_m, edgecolor='black',
                       linewidth=1.2, alpha=0.8)
    ax_m.errorbar(x_pos_m, means_m, yerr=[errors_lower_m, errors_upper_m],
                  fmt='none', ecolor='black', capsize=5, capthick=2, linewidth=2)

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars_m, means_m)):
        height = bar.get_height()
        ax_m.text(bar.get_x() + bar.get_width()/2., height,
                  f'{val:.3f}',
                  ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax_m.set_xlabel('Material Indicators', fontweight='bold', fontsize=13)
    ax_m.set_ylabel('Indicator Value', fontweight='bold', fontsize=13)
    ax_m.set_title('Material Indicators (M) with 95% Confidence Intervals',
                   fontweight='bold', fontsize=14, pad=20)
    ax_m.set_xticks(x_pos_m)
    ax_m.set_xticklabels(m_labels, fontsize=10)
    ax_m.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax_m.set_axisbelow(True)

    plt.tight_layout()
    save_path_m = os.path.join(save_dir, f'mre_material_indicators{suffix}.png')
    plt.savefig(save_path_m, dpi=dpi, bbox_inches='tight')
    print(f"Material indicators plot saved to: {save_path_m}")
    plt.close()

    # ========== PLOT R INDICATORS ==========
    r_indicators = ['R1', 'R2', 'R3', 'R4']
    r_labels = ['R1\n(Reduce)', 'R2\n(Remanufacturing)',
                'R3\n(Repurposing)', 'R4\n(Recycling)']

    fig_r, ax_r = plt.subplots(figsize=(10, 5))

    means_r = [stats[ind]['mean'] for ind in r_indicators]
    errors_lower_r = [stats[ind]['error_bar'][0] for ind in r_indicators]
    errors_upper_r = [stats[ind]['error_bar'][1] for ind in r_indicators]

    colors_r = sns.color_palette("rocket", len(r_indicators))
    x_pos_r = np.arange(len(r_indicators))

    bars_r = ax_r.bar(x_pos_r, means_r, color=colors_r, edgecolor='black',
                       linewidth=1.2, alpha=0.8)
    ax_r.errorbar(x_pos_r, means_r, yerr=[errors_lower_r, errors_upper_r],
                  fmt='none', ecolor='black', capsize=5, capthick=2, linewidth=2)

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars_r, means_r)):
        height = bar.get_height()
        ax_r.text(bar.get_x() + bar.get_width()/2., height,
                  f'{val:.3f}',
                  ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax_r.set_xlabel('Recovery Indicators', fontweight='bold', fontsize=13)
    ax_r.set_ylabel('Indicator Value', fontweight='bold', fontsize=13)
    ax_r.set_title('Recovery Indicators (R) with 95% Confidence Intervals',
                   fontweight='bold', fontsize=14, pad=20)
    ax_r.set_xticks(x_pos_r)
    ax_r.set_xticklabels(r_labels, fontsize=11)
    ax_r.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax_r.set_axisbelow(True)

    plt.tight_layout()
    save_path_r = os.path.join(save_dir, f'mre_recovery_indicators{suffix}.png')
    plt.savefig(save_path_r, dpi=dpi, bbox_inches='tight')
    print(f"Recovery indicators plot saved to: {save_path_r}")
    plt.close()

    # ========== PLOT E INDICATORS ==========
    e_indicators = ['E1', 'E2', 'E3', 'E4']
    e_labels = ['E1\n(Renewable\nEnergy)', 'E2\n(Energy\nEfficiency)',
                'E3\n(Recycling/EOL\nConsumption)', 'E4\n(Energy\nReturn)']

    fig_e, ax_e = plt.subplots(figsize=(10, 5))

    means_e = [stats[ind]['mean'] for ind in e_indicators]
    errors_lower_e = [stats[ind]['error_bar'][0] for ind in e_indicators]
    errors_upper_e = [stats[ind]['error_bar'][1] for ind in e_indicators]

    colors_e = sns.color_palette("mako", len(e_indicators))
    x_pos_e = np.arange(len(e_indicators))

    bars_e = ax_e.bar(x_pos_e, means_e, color=colors_e, edgecolor='black',
                       linewidth=1.2, alpha=0.8)
    ax_e.errorbar(x_pos_e, means_e, yerr=[errors_lower_e, errors_upper_e],
                  fmt='none', ecolor='black', capsize=5, capthick=2, linewidth=2)

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars_e, means_e)):
        height = bar.get_height()
        ax_e.text(bar.get_x() + bar.get_width()/2., height,
                  f'{val:.3f}',
                  ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax_e.set_xlabel('Energy Indicators', fontweight='bold', fontsize=13)
    ax_e.set_ylabel('Indicator Value', fontweight='bold', fontsize=13)
    ax_e.set_title('Energy Indicators (E) with 95% Confidence Intervals',
                   fontweight='bold', fontsize=14, pad=20)
    ax_e.set_xticks(x_pos_e)
    ax_e.set_xticklabels(e_labels, fontsize=11)
    ax_e.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax_e.set_axisbelow(True)

    plt.tight_layout()
    save_path_e = os.path.join(save_dir, f'mre_energy_indicators{suffix}.png')
    plt.savefig(save_path_e, dpi=dpi, bbox_inches='tight')
    print(f"Energy indicators plot saved to: {save_path_e}")
    plt.close()

    return save_path_m, save_path_r, save_path_e


def save_to_cumulative_csv(stats):
    """
    Save MRE results to cumulative_results_indicators.csv

    Args:
        stats: Dictionary containing statistics from Monte Carlo simulation
    """
    import csv

    # Path to cumulative CSV (in parent directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cumulative_csv_path = os.path.join(script_dir, '..', f'cumulative_results_indicators{SUF}.csv')

    try:
        # Check if file exists to determine if we need headers
        file_exists = os.path.exists(cumulative_csv_path)

        # Read existing data if file exists
        existing_data = {}
        if file_exists:
            with open(cumulative_csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_data[row['Indicator']] = row

        # Update with MRE data (using total_M, total_R, total_E)
        for indicator in ['total_M', 'total_R', 'total_E']:
            # Map to display names
            display_name = indicator.replace('total_', '').upper()  # M, R, E

            existing_data[display_name] = {
                'Indicator': display_name,
                'Mean': f'{stats[indicator]["mean"]:.6f}',
                'CI_Lower': f'{stats[indicator]["lower_ci"]:.6f}',
                'CI_Upper': f'{stats[indicator]["upper_ci"]:.6f}'
            }

        # Write back to CSV
        with open(cumulative_csv_path, 'w', newline='') as f:
            fieldnames = ['Indicator', 'Mean', 'CI_Lower', 'CI_Upper']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for indicator in ['PCI', 'CI', 'CEI', 'ECPI', 'M', 'R', 'E']:
                if indicator in existing_data:
                    writer.writerow(existing_data[indicator])

        print(f"\nMRE results saved to {cumulative_csv_path}")

    except PermissionError:
        print(f"\nWARNING: Could not write to {cumulative_csv_path}")
        print("The file may be open in another program (e.g., Excel).")
        print("Please close the file and run the script again to save results.")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("MRE INDICATOR CALCULATION RESULTS")
    print("="*70)

    print("\nMaterial Indicators (M):")
    print("-" * 70)
    print(f"M1 (Material Circularity Inflow):              {M1_value:.6f}")
    print(f"M2 (Material Recovery Importance):             {M2_value:.6f}")
    print(f"M3 (Product Material Recovery Potential):      {M3_value:.6f}")
    print(f"M4 (Regional Material Recovery Cooperation):   {M4_value:.6f}")
    print(f"M5 (Material Recovery Rates from Distance):    {M5_value:.6f}")
    print(f"M6 (Water Circularity):                        {M6_value:.6f}")
    print(f"M7 (Weight of Material Outflow):               {M7_value:.6f}")
    print(f"\nTotal M:                                        {total_M_value:.6f}")

    print("\nRecovery Indicators (R):")
    print("-" * 70)
    print(f"R1 (Reduce):                                    {R1_value:.6f}")
    print(f"R2 (Remanufacturing):                           {R2_value:.6f}")
    print(f"R3 (Repurposing-Echelon Utilization):          {R3_value:.6f}")
    print(f"R4 (Recycling):                                 {R4_value:.6f}")
    print(f"\nTotal R:                                        {total_R_value:.6f}")

    print("\nEnergy Indicators (E):")
    print("-" * 70)
    print(f"E1 (Share of Renewable Energy):                 {E1_value:.6f}")
    print(f"E2 (Energy Efficiency):                         {E2_value:.6f}")
    print(f"E3 (Energy Consumption in Recycling/EOL):       {E3_value:.6f}")
    print(f"E4 (Energy Return Indicator):                   {E4_value:.6f}")
    print(f"\nTotal E:                                        {total_E_value:.6f}")
    print("="*70)

    # Run Monte Carlo simulation and plot
    print("\n" + "="*70)
    print("MONTE CARLO SIMULATION WITH ERROR BARS")
    print("="*70)
    fig, ax, stats = plot_mre_with_error_bars(n_samples=1000, uncertainty_pct=0.05,
                                              save_path=f'mre_with_error_bars{SUF}.png')

    # Plot individual indicators
    print("\n" + "="*70)
    print("PLOTTING INDIVIDUAL INDICATORS")
    print("="*70)
    plot_individual_indicators(stats, suffix=SUF)

    # Save to cumulative CSV
    save_to_cumulative_csv(stats)

    print("\n" + "="*70)
    print("ALL TASKS COMPLETED SUCCESSFULLY!")
    print("="*70)


