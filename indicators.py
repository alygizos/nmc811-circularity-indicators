from typing import Sequence
import math

# ==========================================================================================================================================================================
# ========================================================================= PCI ============================================================================================
# ==========================================================================================================================================================================

def compute_final_pci():
    Total_EVB_Mass = 181.4 # BRAWS data [kg]

    # ================== STEEL =====================

    def compute_pci_steel():
        
        # ============= CONSTANTS =====================
        
        M = 20.0 # BRAWS data [kg]
        F_u = 0.0
        F_r = 0.95
        C_u = 0.0
        C_r = 1.0
        E_cp = 0.815
        E_fp = 0.85
        C_fp = 0.5
        C_cp = 0.5
        E_ms = 0.99
        E_rfp = 1.0 # BRAWS data
        X = 1.0

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
        return PCI

    # ================== ALUMINIUM =====================

    def compute_pci_aluminium():
        
        # ============= CONSTANTS =====================
        
        M = 35.0 # BRAWS data [kg]
        F_u = 0.0
        F_r = 1.0
        C_u = 0.0
        C_r = 1.0
        E_cp = 0.85
        E_fp = 1.0
        C_fp = 0.9
        C_cp = 0.9
        E_ms = 0.99
        E_rfp = 1.0 # BRAWS data
        X = 1.0

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
        return PCI
 
    # ================== GRAPHITE =====================

    def compute_pci_graphite():
        
        # ============= CONSTANTS =====================
        
        M = 52.0 # BRAWS data [kg]
        F_u = 0.0
        F_r = 0.935
        C_u = 0.0
        C_r = 1.0
        E_cp = 0.85
        E_fp = 1.0
        C_fp = 0.5
        C_cp = 0.5
        E_ms = 0.99
        E_rfp = 0.95 # BRAWS data
        X = 1.0

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
        return PCI
  
    # ================== COPPER =====================

    def compute_pci_copper():
        
        # ============= CONSTANTS =====================
        
        M = 20.0 # BRAWS data [kg]
        F_u = 0.0
        F_r = 0.96
        C_u = 0.0
        C_r = 1.0
        E_cp = 0.96
        E_fp = 0.98
        C_fp = 0.5
        C_cp = 0.5
        E_ms = 0.99
        E_rfp = 1.0 # BRAWS data
        X = 1.0

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
        return PCI

    # ================== COBALT =====================

    def compute_pci_cobalt():
        
        # ============= CONSTANTS =====================
        
        M = 8.0 # BRAWS data [kg]
        F_u = 0.0
        F_r = 0.84
        C_u = 0.0
        C_r = 1.0
        E_cp = 1.0
        E_fp = 0.45
        C_fp = 0.5
        C_cp = 0.5
        E_ms = 0.99
        E_rfp = 0.995 # BRAWS data
        X = 1.0

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
        return PCI
   
    # ================== NICKEL =====================

    def compute_pci_nickel():
        
        # ============= CONSTANTS =====================
        
        M = 29.0 # BRAWS data [kg]
        F_u = 0.0
        F_r = 0.84
        C_u = 0.0
        C_r = 1.0
        E_cp = 1.0
        E_fp = 0.94
        C_fp = 0.5
        C_cp = 0.5
        E_ms = 0.99
        E_rfp = 0.995 # BRAWS data
        X = 1.0

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
        return PCI

    # ================== MANGANESE =====================

    def compute_pci_manganese():
        
        # ============= CONSTANTS =====================
        
        M = 10.0 # BRAWS data [kg]
        F_u = 0.0
        F_r = 0.84
        C_u = 0.0
        C_r = 1.0
        E_cp = 1.0
        E_fp = 0.75
        C_fp = 0.5
        C_cp = 0.5
        E_ms = 0.99
        E_rfp = 0.995 # BRAWS data
        X = 1.0

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
        return PCI
     
    # ================== LITHIUM =====================

    def compute_pci_lithium():
        
        # ============= CONSTANTS =====================
        
        M = 6.0 # BRAWS data [kg]
        F_u = 0.0
        F_r = 0.91
        C_u = 0.0
        C_r = 1.0
        E_cp = 1.0
        E_fp = 0.62
        C_fp = 0.5
        C_cp = 0.5
        E_ms = 0.99
        E_rfp = 0.95 # BRAWS data
        X = 1.0

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
        return PCI
        
    # ================ FINAL PCI ===========================

    pcis = {
        "steel":     compute_pci_steel(),
        "aluminium": compute_pci_aluminium(),
        "graphite":  compute_pci_graphite(),
        "copper":    compute_pci_copper(),
        "cobalt":    compute_pci_cobalt(),
        "nickel":    compute_pci_nickel(),
        "manganese": compute_pci_manganese(),
        "lithium":   compute_pci_lithium(),
    }

    masses = {
        "steel": 20.0,
        "aluminium": 35.0,
        "graphite": 52.0,
        "copper": 20.0,
        "cobalt": 8.0,
        "nickel": 29.0,
        "manganese": 10.0,
        "lithium": 6.0,
    }

    FINAL_PCI = sum(pcis[k] * masses[k] for k in masses) / Total_EVB_Mass

    return FINAL_PCI, pcis

# ==========================================================================================================================================================================
# ========================================================================= CEI ============================================================================================
# ==========================================================================================================================================================================

def compute_cei_di_maio(materials):
    
    """
    Circular Economy Index (CEI) from Di Maio & Rem (2015)

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

    # DATA  

materials = [
    {'mass_required': 20, 'mass_recycled': 18, 'price_primary': 5.0, 'price_recycled': 4.2},
    {'mass_required': 10, 'mass_recycled': 6,  'price_primary': 10.0, 'price_recycled': 8.0},
]

# ==========================================================================================================================================================================
# ========================================================================= CI =============================================================================================
# ==========================================================================================================================================================================

def compute_ci_cullen(alpha=None, beta=None,
                      recovered_eol=None, total_demand=None,
                      energy_recovery=None, energy_primary=None):
    """
    Circularity Index (Cullen, 2017)
    Combines material quantity (alpha) and quality/energy (beta) effects.

    α = recovered EOL material / total material demand
    β = 1 - (energy required to recover material / energy required for primary production)
    CI = α × β

    Parameters
    ----------
    alpha : float, optional
        Precomputed α value. If None, computed from recovered_eol/total_demand.
    beta : float, optional
        Precomputed β value. If None, computed from energy_recovery/energy_primary.
    recovered_eol : float, optional
        Mass of recovered EOL material [kg or t].
    total_demand : float, optional
        Total material demand [kg or t].
    energy_recovery : float, optional
        Energy required to recover material [MJ/kg].
    energy_primary : float, optional
        Energy required for primary production [MJ/kg].

    Returns
    -------
    float
        Circularity Index (CI) between 0 and 1.
    """
    
# compute alpha
    if alpha is None:
        if recovered_eol is None or total_demand in (None, 0):
            raise ValueError("Provide either alpha or recovered_eol and total_demand.")
        alpha = recovered_eol / total_demand

    if beta is None:
        if energy_recovery is None or energy_primary in (None, 0):
            raise ValueError("Provide either beta or energy_recovery and energy_primary.")
        beta = 1 - (energy_recovery / energy_primary)

    ci = alpha * beta
    return max(0.0, min(ci, 1.0))


# --- helper so print_results can call it ---
def compute_ci_cullen_aluminum():
    """Returns the CI for aluminum using Cullen (2017) data."""
    return compute_ci_cullen(
        recovered_eol=11,
        total_demand=54,
        energy_recovery=7.6,
        energy_primary=174
    )

# ==========================================================================================================================================================================
# ========================================================================= ECPI ===========================================================================================
# ==========================================================================================================================================================================

def compute_ecpi(m_in_circular, m_in_virgin,
                 m_out_circular, m_out_linear,
                 LCA_emissions_circular, LCA_emissions_linear):
    
    """
    ECPI (Carmona Aparicio et al., 2025)

    α_in  = m_in_circular / (m_in_circular + m_in_virgin)
    α_out = m_out_circular / (m_out_circular + m_out_linear)
    α     = α_in * α_out
    β     = 1 - (LCA_emissions_circular / LCA_emissions_linear)
    ECPI  = α * β
    """
    
    alpha_inflow = m_in_circular / (m_in_circular + m_in_virgin)
    alpha_out    = m_out_circular / (m_out_circular + m_out_linear)
    alpha        = alpha_inflow * alpha_out
    beta         = 1 - (LCA_emissions_circular / LCA_emissions_linear)
    ecpi         = alpha * beta
    return ecpi, alpha_inflow, alpha_out, beta

# DATA

def compute_ecpi_example():
    """Returns ECPI for sample system (Aparicio et al., 2025)."""
    m_in_circular, m_in_virgin = 220, 780
    m_out_circular, m_out_linear = 910, 90
    LCA_emissions_circular, LCA_emissions_linear = 0.29, 0.49

    ecpi, ain, aout, b = compute_ecpi(
        m_in_circular, m_in_virgin,
        m_out_circular, m_out_linear,
        LCA_emissions_circular, LCA_emissions_linear
    )
    return ecpi, ain, aout, b

# ==========================================================================================================================================================================
# ========================================================================= M,R,E ==========================================================================================
# ==========================================================================================================================================================================

    # Data (To be changed)

# Material Indicators
# M1
m_re = 50                                                                       # recycled material mass
m_vir = 150                                                                     # virgin material mass
F = [0.06, 0.25, 0.10, 0.15, 0.44]                                              # Mass fraction of material i
P_i = [60, 25, 40, 5, 10]                                                       # Average price of the material [$/kg]
P_m = 5                                                                         # Price of manganese used as a benchmark [$/kg]
f_env = [0.8, 0.6, 0.7, 0.4, 0.3]                                               # Environmental impact
m_i       = [5, 3, 2]                                                           # kg of Ni, Co, Li
F_pyro    = [0.7, 0.5, 0.0]
eta_pyro  = [0.9, 0.8, 0.0]
F_hydro   = [0.3, 0.5, 1.0]
eta_hydro = [0.95, 0.85, 0.9]
m_c_i     = [100, 200, 150]                                                     # Mass of materials recycled within the region [kg/year]
m_out_c_i = [50, 100, 50]                                                       # Mass of materials recycled outside the region [kg/year]
C_trans = [0.4, 0.6, 0.8]                                                       # Transportation expenses for a unit material [$/kg]
C_energy = [0.2, 0.3, 0.4]                                                      # Energy costs [$/kg]
C_labor = [0.1, 0.1, 0.2]                                                       # Labor costs [$/kg]
C_total = [2.0, 2.5, 3.0]                                                       # Total costs [$/kg]
V_r = 2000                                                                      # Volume of recycled water [m^3]
V_t = 5000                                                                      # Total water input [m^3]
Vw_treated = 1800                                                               # Volume of treated wastewater [m^3]
Vw = 2000                                                                       # Total volume of wastewater produced [m^3]
m_residuals = 10                                                                # Mass of product residuals in the processing [kg/year]
m_emissions = 5                                                                 # Mass of emissions [kg/year]
m_landfill  = 15                                                                # Mass of landfill waste [kg/year]
m_product   = 200                                                               # Total mass of product [kg/year]

# End of life indicators

# R1
m_waste = 100                                                                   # Amount of waste produced during manufacturing [kg]
m_natural_resources = 300                                                       # Utilization of natural resources during production [kg]
m_product = 500                                                                 # Mass of the final product [kg]

# R2
m_remanufactured = 1200                                                         # Mass of remanufactured batteries [kg/year]
F_EV = 0.40                                                                     # Fraction of remanufactured batteries returned to EV use            
F_generation = 0.25                                                             # Fraction used for generation-side energy storage    
F_user = 0.20                                                                   # Fraction used for user-side energy storage          
F_mobile = 0.10                                                                 # Fraction used for mobile power supply       
m_product = 2500                                                                # Total mass of the product [kg/year]     
m_recycled_at_80 = 300                                                          # Mass of batteries recycled when their state of health (SOH) is below 80 % [kg/year]

# R3
SOF_retired = [0.6, 0.5, 0.4]                                                   # State of function of the battery following secondary use (State of health)
Y_retired = [8, 6, 4]                                                           # Lifespan of the battery in secondary use [years]
m_repurpose = [400, 300, 200]                                                   # Mass of batteries repurposed in pathway i [kg/year]
m_product = 2000                                                                # Total mass of the product [kg/year]

# R4 
recycled_fraction = 0.75                                                        # Fraction of the battery that can be potentially recycled based on the strategies employed by companies in the battery life cycle
qualitative_scores = [0.8, 0.9, 0.7, 0.6, 0.9, 0.8, 0.7, 0.9, 0.8]              # The average of nine equally weighted questions from the questionnaire in Table S3

# E1
F_rene = [0.25, 0.40, 0.20, 0.15]                                               # Importance fraction for step i
E_rene = [200, 350, 80, 250]                                                    # Renewable energy consumption
E_total = [1000, 1200, 800, 500]                                                # Total energy consumption

# E2
F_step = [0.15, 0.15, 0.35, 0.35]                                               # Fraction of energy consumption in step i
ES_step = [0.2, 0.1, 0.05, 0.15]                                                # Energy-saving factor related to reference technologies (Drying of electrode, cell formation etc)

# E3
E_extraction = 1200                                                             # Energy for raw material extraction [MJ]
E_processing = 1500                                                             # Energy for material processing [MJ]
E_assembly = 800                                                                # Energy for module/cell assembly [MJ]
E_transport_manuf = 200                                                         # Energy for manufacturing transport [MJ]
E_collection = 150                                                              # Energy for collection of spent batteries [MJ]
E_transport_recy = 100                                                          # Energy for transport to recycling facility [MJ]
E_pre_treatment = 400                                                           # Energy for pre-treatment (disassembly/shredding) [MJ]
E_recovery = 800                                                                # Energy for recovery processes [MJ]
E_repurpose = 300                                                               # Energy for repurposing into second-life applications [MJ]
E_operational_secondlife = 500                                                  # Operational energy during second-life use [MJ]
f_saving_from_recycled = 0.3                                                    # Energy saving factor from recycled material [0–1]
P_recycling = 0.5                                                               # Fraction of total energy allocated to recycling
P_secondlife = 0.3                                                              # Fraction of total energy allocated to second-life use
Y_retired_years = 10                                                            # Battery retired year [years]
service_life_primary_years = 8.0                                                # Average service life for an EV battery [years]

# E4 
E_used_j = [12000, 1500]                                                        # Average energy usage [MJ/yr]
eta0 = 0.92                                                                     # efficiency factor
t_j = [8, 3]                                                                    # Service life [years]
F_j = [0.90, 0.10]                                                              # Fraction of product for battery function j
I_j = [1.0, 0.5]                                                                # Importance factor
QP_ipf = [1800, 900, 300]                                                       # Average annual energy required for production [MJ/yr]
QT_ipf = [200, 150]                                                             # Average annual energy required for transportation [MJ/yr]

beta_i = [0.6, 0.6, 0.6]                                                        # Estimated proportion of primary fossil energy used to generate the electricity used in the production of component i

    # Conversion factors
alpha_pf_el = 2.5                                                               # primary fossil → electricity
alpha_el_el = 1.0
alpha_pf_th = 1.2                                                               # primary fossil → thermal
alpha_el_th = 1.0
alpha_pf_tr = 1.4                                                               # primary fossil → transport work
alpha_el_tr = 1.0

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


def M2(F: Sequence[float], f_price: Sequence[float] = None, f_env: Sequence[float] = None,         # M2 Material Recovery Importance
       P_i: Sequence[float] = None, P_m: float = None) -> float:
    
    """
    M2 = sum_i F_i * (f_price_i + f_env_i)/2
    F_i: mass fraction of material i (sum = 1)
    f_price_i: price factor (P_i / P_m) --> provide P_i and P_m
    f_env_i: environmental impact factor for material i (0–1 or normalized)
    """
    
    F = list(map(float, F))
    if f_price is None and P_i is not None and P_m not in (None, 0):
        f_price = [float(p)/float(P_m) for p in P_i]
    if f_price is None and f_env is None:
        return float("nan")
    if f_price is None:
        factors = list(map(float, f_env))
    elif f_env is None:
        factors = list(map(float, f_price))
    else:
        factors = [(float(a)+float(b))/2.0 for a,b in zip(f_price, f_env)]
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
    return sum(mi * ri for mi, ri in zip(m_i, rec))


def M4(m_c_i: Sequence[float], m_out_c_i: Sequence[float]) -> float:                                # M4 Regional material recovery cooperation
                               
    """
    M4 = sum_i m_c,i / (sum_i m_c,i + sum_i m_out,c,i)
    m_c,i: mass recovered within region
    m_out,c,i: mass recovered outside region
    """
    
    in_region = sum(map(float, m_c_i))
    out_region = sum(map(float, m_out_c_i))
    return _safe_div(in_region, in_region + out_region)

 
def M5(m_c_i: Sequence[float], m_out_ci: Sequence[float],                                           # M5 Material recovery rates from cooperation in distance
       C_trans: Sequence[float], C_energy: Sequence[float],
       C_labor: Sequence[float], C_total: Sequence[float]) -> float:
    
    """
    M5 = sum_{c,i} [ m_out,c,i * (1 - D_ci) ] / ( sum_i m_c,i + sum_i m_out,c,i )
    where D_ci = (C_trans + C_energy + C_labor) / C_total

    m_c,i: mass recovered within region
    m_out,c,i: mass recovered outside region
    C_trans, C_energy, C_labor: cost components [$/kg]
    C_total: total cost per material [$/kg]
    """
    
    D_ci = [_safe_div(float(ct) + float(ce) + float(cl), float(ctot))
            for ct, ce, cl, ctot in zip(C_trans, C_energy, C_labor, C_total)]

    in_region = sum(map(float, m_c_i))
    out_total = sum(map(float, m_out_ci))
    effective_out = sum(float(mo) * (1.0 - float(d)) for mo, d in zip(m_out_ci, D_ci))
    return _safe_div(effective_out, in_region + out_total)


def M6(V_r: float, V_t: float, Vw_treated: float, Vw: float) -> float:                              # M6 Water circularity
    
    """
    WRR = V_r / V_t
    WTE = Vw_treated / Vw
    M6  = WRR * WTE
    V_r: recycled/reused water volume
    V_t: total water input
    Vw_treated: treated wastewater volume
    Vw: total wastewater volume
    """
    
    WRR = _safe_div(V_r, V_t)
    WTE = _safe_div(Vw_treated, Vw)
    if math.isnan(WRR) or math.isnan(WTE):
        return float("nan")
    return WRR * WTE


def M7(m_residuals: float, m_emissions: float, m_landfill: float, m_product: float) -> float:       # M7 Weight of material outflow
    
    """
    M7 = 1 - (m_residuals + m_emissions + m_landfill) / m_product
    m_residuals: residual mass
    m_emissions: emitted mass-equivalent
    m_landfill: mass to landfill
    m_product: product/processed mass baseline
    """
    
    return 1.0 - _safe_div(m_residuals + m_emissions + m_landfill, m_product)

                                                                                                    # End of life indicators

def R1_mass(m_waste: float, m_natural_resources: float, m_product: float) -> float:                 # R1 Reduce
    
    """
    R1 = ((1 - m_waste) * (1 - m_natural_resources)) / m_product
    All inputs in kg
    """
    
    if m_product <= 0:
        return float("nan")
    val = ((1 - m_waste) * (1 - m_natural_resources)) / m_product
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
                                                                                                                                         
def E1(F_rene: Sequence[float], E_rene: Sequence[float], E_total: Sequence[float]) -> float:            # E1 Share if renewable energy
    
    """
        Re_i = E_rene_i / E_total_i
    E1   = Σ_i (F_rene_i * Re_i)
       
    """
    
    if not (len(F_rene) == len(E_rene) == len(E_total)):
        raise ValueError("F_rene, E_rene, and E_total must have the same length.")
    return sum(f * (Er / Et) for f, Er, Et in zip(F_rene, E_rene, E_total))



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
