"""
lfp_greet_data.py  -  SINGLE SOURCE OF TRUTH for LFP inputs
===========================================================
Every value below is tagged with its provenance so the analysis is fully
auditable.  Provenance tags:

  [GREET-LFP]   LFP-specific value read from R&D GREET2 2024 Rev1
  [GREET-GEN]   chemistry-independent GREET intensity (same for any cathode)
  [LIT]         literature / EverBatt / USGS value (cited)
  [ASSUMP]      process assumption, not chemistry-specific (no GREET source)

GREET file: Literature/NMC811/RD GREET2024_Rev1/R&D GREET2024_Rev1/
            R&D GREET2_2024_Rev1.xlsm
"""

# ===========================================================================
# A. PACK BASIS                                                    [GREET-LFP]
# ===========================================================================
NMC_PACK_KG = 438.23520640359334   # GREET NMC811 reference pack mass
NMC_SE_WHKG = 197.69               # Battery_Sum sec.8  (NMC811, 300-mile)
LFP_SE_WHKG = 142.89               # Battery_Sum sec.8  (LFP,    300-mile)
PACK_ENERGY_KWH = NMC_PACK_KG * NMC_SE_WHKG / 1000.0   # ~86.6 kWh (held constant)
PACK_KG = PACK_ENERGY_KWH * 1000.0 / LFP_SE_WHKG       # LFP pack mass

# ===========================================================================
# B. COMPOSITION  (% mass, EV 300-mile, LFP Hydrothermal)          [GREET-LFP]
#    Battery_Sum sec.7 (rows 638+). Hydro & Solid-State are identical here.
# ===========================================================================
COMP = {
    'active_material'    : 0.2759, 'graphite'        : 0.1418,
    'binder'             : 0.0086, 'copper'          : 0.1012,
    'wrought_aluminum'   : 0.1251, 'lipf6'           : 0.0127,
    'ethylene_carbonate' : 0.0352, 'dimethyl_carbonate': 0.0352,
    'polypropylene'      : 0.0008, 'polyethylene'    : 0.0105,
    'polymer'            : 0.0083, 'pet'             : 0.0018,
    'steel'              : 0.1373, 'stainless_steel' : 0.0583,
    'ceramic'            : 0.0003, 'thermal_insulation': 0.0031,
    'coolant_glycol'     : 0.0372, 'electronic_parts': 0.0067,
}

# LiFePO4 elemental fractions (g/mol: Li 6.941, Fe 55.845, P 30.9738, O4 63.996)
_MM = 6.941 + 55.845 + 30.9738 + 4*15.999
FRAC = {'Li': 6.941/_MM, 'Fe': 55.845/_MM, 'P': 30.9738/_MM, 'O': 4*15.999/_MM}

# ===========================================================================
# C. CHEMISTRY-INDEPENDENT MATERIAL INTENSITIES                    [GREET-GEN]
#    GREET "4.3 Li-Ion" block:  energy mmBtu/lb,  GHG g/lb.
#    (Copper production energy is the same regardless of cathode chemistry.)
# ===========================================================================
MMBTU_TO_MJ = 1055.06
LB_PER_KG   = 2.2046226218
# energy mmBtu/lb , ghg g/lb
INTENSITY = {  # composition-key : (energy_mmBtu_per_lb, ghg_g_per_lb)
    'graphite'          : (0.04240373602441295, 3979.197779594231),
    'binder'            : (0.015024859212790093, 932.9658016044398),
    'copper'            : (0.02529241569205385, 1750.8134101429453),
    'wrought_aluminum'  : (0.05055100357961031, 3498.5912097593496),
    'lipf6'             : (0.07318032167202113, 4395.10047443441),
    'ethylene_carbonate': (0.004292678448264806, 156.2795113629457),
    'dimethyl_carbonate': (0.015778523924572917, 580.4591878866729),
    'polypropylene'     : (0.031975325941955714, 720.1251658777298),
    'polyethylene'      : (0.03289092681365955, 855.6161662626236),
    'polymer'           : (0.03682933975737526, 1517.274862370974),
    'pet'               : (0.031769896472854005, 1004.2371188351699),
    'steel'             : (0.011983263369553422, 1068.8308117642443),
    'stainless_steel'   : (0.0057242512774149535, 361.97131367531927),
    'thermal_insulation': (0.011149298140806367, 773.3003185815124),
    'coolant_glycol'    : (0.009741945277430336, 254.15066090736292),
    'electronic_parts'  : (0.1643838353441709, 9968.616609074114),
    'ceramic'           : (0.011149298140806367, 773.3003185815124),  # ~insulation proxy
}
# Battery assembly (per kWh, chemistry-independent)               [GREET-GEN]
ASSEMBLY_MMBTU_PER_KWH = 0.2000486913208543     # Battery_Assembly
ASSEMBLY_GHG_G_PER_KWH = 12467.587277243007     # GHGs g/kWh

# ===========================================================================
# D. LFP ACTIVE-MATERIAL (LiFePO4) CRADLE-TO-GATE                  [GREET-LFP]
#    Cathode recipe ton/ton LiFePO4 (Battery_Sum 9.2 / Other_Cathodes) and
#    precursor production intensities (Other_Cathodes cathode-precursor block):
#      energy mmBtu/ton , GHG t CO2/ton
# ===========================================================================
# precursor : (ton per ton LiFePO4, energy_mmBtu_per_ton, ghg_tCO2_per_ton)
LFP_CATHODE = {
    'hydro': {
        'recipe': {  # ton/ton LiFePO4
            'LiOH'  : (0.26838, 248.90, 20.539),   # Other_Cathodes col16
            'H3PO4' : (0.36606, 14.625, 0.965),    # Other_Cathodes col18
            'FeSO4' : (0.56745, 0.0,    0.0),       # GREET treats FeSO4 as byproduct (0)
            'NMP'   : (0.007,   328.77, 18.0),     # Battery_Materials NMP (CO2 approx)
        },
        'synthesis': (34.21678, 1.989),            # Battery_Sum 9.4 LFP Hydrothermal
    },
    'solid': {
        'recipe': {  # ton/ton LiFePO4
            'Li2CO3': (0.23419, 115.489, 10.726),  # [GREET-LFP] Other_Cathodes/Li_Chemicals: 115.489 mmBtu/ton
                                                   # (=37.176 kWh/kg), CO2 10.726 t/ton (CO2 row, same basis as LiOH 20.539).
                                                   # Corrects an earlier wrong placeholder (44.42 / 3.640) [2026-06-20].
            'Fe3O4' : (0.48922, 1.11,  0.10),      # iron oxide (low)
            'DAP'   : (0.83708, 18.49, 1.20),      # diammonium phosphate
            'NMP'   : (0.007,   328.77, 18.0),
        },
        'synthesis': (4.96508, 0.277),             # Battery_Sum 9.4 LFP Solid-State
    },
}

def active_material_intensity(route):
    """Return (energy_mmBtu_per_ton, ghg_tCO2_per_ton) for LiFePO4 cradle-to-gate."""
    d = LFP_CATHODE[route]
    e = d['synthesis'][0]; g = d['synthesis'][1]
    for _, (tpt, en, gh) in d['recipe'].items():
        e += tpt*en; g += tpt*gh
    return e, g   # mmBtu/ton , t CO2/ton

# ===========================================================================
# H. CI ENERGY BASIS  (mirrors the NMC811 CI structure)            [GREET-LFP]
#    Cell-level = cathode precursors + cell Al + cell Cu  (NO graphite).
#    Pack-level = steel + aluminium (recyclable module+pack).
#    Recycling process = HYDROMETALLURGICAL (same as NMC811).
#    Precursor production energy: GREET Other_Cathodes (mmBtu/ton).
#    mmBtu/ton -> kWh/kg uses the NMC811 calibration factor (Li2CO3 115.356
#    mmBtu/ton -> 37.133 kWh/kg => 0.321883) so values match the NMC811 basis.
# ===========================================================================
MMBTU_TON_TO_KWHKG = 0.321883
CI_PRECURSORS = {  # route : {name : (ton/ton LiFePO4, prod energy mmBtu/ton, recovers->material|None)}
    # NMP (solvent) excluded from CI per analysis decision (not a recovered cell material).
    'hydro': {'LiOH' :(0.26838, 248.90, 'lithium'),
              'H3PO4':(0.36606, 14.625, 'phosphorus'),
              'FeSO4':(0.56745, 0.0,    'iron')},
    'solid': {'Li2CO3':(0.23419, 115.489, 'lithium'),   # corrected GREET energy (was wrong 44.42); 115.489 mmBtu/ton = 37.176 kWh/kg
              'Fe3O4' :(0.48922, 1.11,  'iron'),
              'DAP'   :(0.83708, 18.49, 'phosphorus')},
}
# cell Al / Cu and pack steel / Al production energies (kWh/kg) — NMC811 CI basis,
# "GREET 2024 Rev1". Chemistry-independent (reused verbatim).
CI_CELL_AL_KWHKG = 27.40256302
CI_CELL_CU_KWHKG = 7.41247533
CI_PACK_STEEL = (4.279660138, 1.371658926)   # (virgin, recycling)
CI_PACK_AL    = (27.40256302, 4.823156931)   # (virgin, recycling)
CI_CELL_RECYCLING_MMBTU_TON = 6.35           # [GREET-LFP] Battery Recycling menu: LFP + Mass recycling,
                                             # hydrometallurgical total energy (NMC811 was 27.5 mmBtu/ton)
CI_CELL_RECYCLING_KWHKG = 6.35 * MMBTU_TON_TO_KWHKG   # = 2.044 kWh/kg  (NMC811 was 8.85225)

# ===========================================================================
# I. ECPI BASIS  (per analysis decision)
#    Lithium represented by LiOH (virgin) / Li2CO3 (recycled); NO graphite,
#    NO whole-LiFePO4 (cathode is not recovered in entirety - only Li).
#    Virgin GHG intensities (kg CO2e/kg, AR6 GWP100) from GREET, as tabulated in
#    indicator_input_values_lfp.xlsx ECPI_indicator sheet.
# ===========================================================================
LI2CO3_TO_LIOH = 47.896/73.89  # 0.6482 kg LiOH-equivalent per kg recovered Li2CO3
                               # (Li2CO3 + Ca(OH)2 -> 2 LiOH + CaCO3; 2x23.948 / 73.89)
LIOH_LI_FRAC = 0.2898363120093536      # Li mass fraction in LiOH (MW 23.948)
LI2CO3_LI_FRAC = 0.18787132397720965   # Li mass fraction in Li2CO3 (for salt-equivalent masses) [chem]
ECPI_MATERIALS = ['LiOH','copper','aluminium','steel']
ECPI_VIRGIN_GHG = {            # kg CO2e/kg
    'LiOH'     : 22.677,       # GREET Other_Cathodes LiOH (AR6 GWP100)
    'copper'   : 3.8599,       # GREET 4.3 Li-Ion
    'aluminium': 14.3695,      # GREET 4.3 Li-Ion (primary)
    'steel'    : 2.9691,       # GREET 4.3 Li-Ion
}
# GREET LFP hydrometallurgical recycling (mass allocation):
LFP_CELL_RECYCLING_GHG   = 0.7890436875687847   # kg CO2e/kg battery cell recycled (hydromet)
LFP_LI2CO3_RECYCLING_GHG = 1.161600569          # kg CO2e/kg Li2CO3 recovered (mass alloc)
ECPI_RECYCLED_GHG = {          # kg CO2e/kg (recycled-route production)
    # LiOH/Cu/Al [GREET-LFP]: cell recycling 0.789 kg/kg cell -> 317.94 kg CO2e allocated
    #   by mass over the recovered cell materials (LiOH+Cu+cell-Al = 106.5 kg) = uniform
    #   2.985 kg/kg (computed in build_lfp_inputs from the LFP cell weight).
    # steel [LIT]: per-material secondary steel.
    'LiOH'     : None,         # set in build = cell mass-allocated uniform (2.985)
    'copper'   : None,         # set in build = cell mass-allocated uniform
    'aluminium': None,         # set in build = cell mass-allocated uniform
    'steel'    : 0.6481,       # [LIT] secondary steel (per-material)
}
ECPI_IN_CIRC = {'LiOH':0.10,'copper':0.32,'aluminium':0.50,'steel':0.26}  # recycled-content fraction
ECPI_PACK_AL_GHG = 2.3548              # [LIT] secondary (module+pack) Al recycled GHG, kg CO2e/kg
ECPI_STEEL_REC_GHG = 0.6481            # [LIT] secondary steel recycled GHG, kg CO2e/kg
# Iron/phosphorus precursor virgin production GHG (kg CO2e/kg) - GREET Other_Cathodes
# (from the ECPI_indicator precursor reference table). Produced but NOT recovered, so
# these enter BOTH the ECPI linear and circular emissions (no recovery saving).
ECPI_FEP_GHG = {'FeSO4': 0.000333779468, 'H3PO4': 1.0661926600185923}

# ---------------------------------------------------------------------------
# ROUTE-AWARE ECPI CATHODE CARRIERS  (hydro vs solid synthesis route)
# The virgin lithium carrier and the Fe/P precursors differ by synthesis route.
# Only these cathode-precursor entries change between routes; Cu/Al/steel and
# the (hydrometallurgical) recycling allocation are route-independent.
# ---------------------------------------------------------------------------
# Lithium carrier per route:
#   name        : ECPI material label
#   recipe_ratio: ton carrier / ton LiFePO4 (drives LINEAR virgin mass)
#   li_frac     : Li mass fraction in the carrier (drives in-cell recoverable mass)
#   virgin_ghg  : virgin production GHG, kg CO2e/kg carrier
#   in_circ     : recycled-content inflow fraction (route-independent = 0.10)
ECPI_LI_CARRIER = {
    'hydro': {'name': 'LiOH',   'recipe_ratio': 0.26838, 'li_frac': LIOH_LI_FRAC,
              'virgin_ghg': 22.677,        # [GREET-LFP] curated AR6 GWP100 (ECPI_indicator sheet anchor)
              'in_circ': 0.10},
    'solid': {'name': 'Li2CO3', 'recipe_ratio': 0.23419, 'li_frac': LI2CO3_LI_FRAC,
              'virgin_ghg': 11.84077363,   # [GREET-LFP] Li2CO3 virgin GHG, AR6 GWP100 basis consistent with
                                           # the LiOH anchor (= 22.677 x CO2-ratio 10.726/20.539) [USER 2026-06-20].
              'in_circ': 0.10},
}
# Cathode Fe/P precursors per route (produced virgin, NOT recovered -> enter BOTH
# the ECPI linear and circular emissions; in_circ = 0). GHG = kg CO2e/kg precursor.
ECPI_FEP = {
    'hydro': {'FeSO4': (0.56745, ECPI_FEP_GHG['FeSO4']),    # 0.000333779468
              'H3PO4': (0.36606, ECPI_FEP_GHG['H3PO4'])},   # 1.0661926600185923
    'solid': {'Fe3O4': (0.48922, 0.10),     # [GREET-LFP recipe-block CO2 proxy] iron oxide (low); pending AR6 figure
              'DAP'  : (0.83708, 1.20)},     # [GREET-LFP recipe-block CO2 proxy] diammonium phosphate; pending AR6 figure
}
# OWinjobi 2020 Table 8 (LFP, BEV): cell aluminium share of total aluminium
OWINJOBI_AL_CELL_FRAC = 18.5/71.0      # 0.2606  (cell 18.5 / total 71 kg)
# GREET LFP hydrometallurgical recycling (per ton battery cells recycled)
LFP_RECYCLING_ENERGY_MMBTU_TON = 6.351985514664392   # = CI_CELL_RECYCLING
LFP_RECYCLING_GHG_G_PER_TON_CELL = 715685.8844        # GHGs, hydromet (for reference)

# ---------------------------------------------------------------------------
# [FLAG - to finalise recycled GHG] GREET LFP recycling allocation factors
# (1.6.3 "Allocation Factor Used"): fraction of each material routed to each
# recycling process. Hydrometallurgical recovers Li2CO3 (13.4%) and graphite
# (28.4%); copper via pyro (100%); LFP cathode via direct (58.6%).
# Combined with the per-ton-cell hydro recycling emissions (in the curated
# indicator_input_values_lfp.xlsx ECPI_indicator sheet), these will replace the
# placeholder ECPI_RECYCLED_GHG['LiOH'] once the allocation method is confirmed.
# ---------------------------------------------------------------------------
LFP_RECYCLING_ALLOCATION = {   # material : (pyro, hydro, direct)
    'LFP_cathode': (0.000, 0.000, 0.586),
    'copper'     : (1.000, 0.000, 0.000),
    'graphite'   : (0.000, 0.284, 0.289),
    'Li2CO3'     : (0.000, 0.134, 0.000),
    'CoSO4'      : (0.000, 0.000, 0.000),
    'MnSO4'      : (0.000, 0.000, 0.000),
    'NiSO4'      : (0.000, 0.000, 0.000),
}

# ===========================================================================
# E. MATERIAL RECOVERY EFFICIENCIES  (verified)
#    GREET Battery Recycling sheet is process-yield based; LFP hydromet
#    recovers Li, Cu, Al, graphite, and Fe/P (as FePO4). Values cross-checked
#    against GREET + FHanna 2025 (EST 10.1021/acs.est.xxx) + Argonne EverBatt.
# ===========================================================================
RECOVERY = {  # material : (eta, source_tag, note)
    'lithium'   : (0.91, '[GREET-LFP/LIT]', 'GREET Battery Recycling hydromet Li2CO3 yield; standardized to 0.91 [USER 2026-06-21] (matches build_lfp_mre eta)'),
    'copper'    : (0.96, '[GREET-GEN/LIT]', 'Cu current-collector recovery, GREET/EverBatt'),
    'aluminium' : (0.93, '[GREET-GEN/LIT]', 'Al recovery (module+pack), EverBatt'),
    'steel'     : (0.95, '[LIT]',           'ferrous scrap recovery, standard'),
    'graphite'  : (0.90, '[GREET-LFP]',     'GREET Battery Recycling hydromet graphite yield (LFP)'),
    'iron'      : (0.00, '[DECISION 2026-06-19]', 'Fe NOT recovered in LFP hydromet (-> FePO4/slag). Produced but not recovered; kept as input with recovery=0.'),
    'phosphorus': (0.00, '[DECISION 2026-06-19]', 'P NOT recovered (-> FePO4/slag). Produced but not recovered; kept as input with recovery=0.'),
}

# ===========================================================================
# F. PRICES ($/kg)  virgin / recycled
#    Shared materials: "Price Analysis ... (Virgin vs Recycled)" doc + USGS.
#    Fe/P: literature estimates (FePO4 low value).
# ===========================================================================
PRICE = {  # material : (virgin, recycled, source_tag)
    'aluminium' : (3.30, 1.117477786, '[LIT]  USGS/EverBatt scrap ~34% of primary'),
    'copper'    : (8.80, 7.11,        '[LIT]  price doc (Cu grade A; recycled ~80%)'),
    'lithium'   : (30.0, 8.37,        '[LIT]  price doc (Li carbonate basis)'),
    'steel'     : (1.00, 0.33,        '[LIT]  price doc (sheet; scrap ~33%)'),
    'iron'      : (1.00, 0.30,        '[LIT-EST] battery-grade Fe precursor; FePO4 low recovered value'),
    'phosphorus': (2.50, 1.00,        '[LIT-EST] phosphoric-acid P basis'),
}

# ===========================================================================
# G. COLLECTION EFFICIENCY (base case; swept 70/90/100 in S3)        [ASSUMP]
# ===========================================================================
COLLECTION_BASE = 0.90
# (LI2CO3_LI_FRAC defined above, alongside LIOH_LI_FRAC)
