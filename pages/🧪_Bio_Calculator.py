import streamlit as st
from chempy import Substance

# Formula: Name
PRESET_REAGENTS = {
    "Custom (Your formula)": "",
    "NaCl": "Sodium chloride",
    "Tris (C4H11NO3)": "Tris base",
    "EDTA dihydrate (C10H14N2Na2O8*2H2O)": "EDTA disodium salt",
    "SDS (NaC12H25SO4)": "Sodium dodecyl sulfate",
    "CuSO4*5H2O": "Copper(II) sulfate pentahydrate",
    "MgCl2*6H2O": "Magnesium chloride hexahydrate",
    "KCl": "Potassium chloride",
    "DTT (C4H10O2S2)": "Dithiothreitol",
    "Glucose (C6H12O6)": "D-Glucose",
    "Glycine (C2H5NO2)": "Glycine",
}

def parse_formula_with_chempy(formula_str: str):
    """
    Parsing with chempy.
    Returns (Substance object, molar_mass, error_message).
    """
    if not formula_str or not formula_str.strip():
        return None, None, "Input your formula."
    
    clean_formula = formula_str.strip()
    try:
        substance = Substance.from_formula(clean_formula)
        mw = substance.molar_mass()  # Возвращает float в г/моль
        return substance, mw, None
    except Exception as e:
        return None, None, f"ERRRORRRR '{clean_formula}': {str(e)}"

def render_molarity_calculator():
    st.header("🧪 Advanced Solution & Molarity Calculator")
    st.caption("Powered by ChemPy — Automated formula parsing, unit conversion & recipe generation.")

    tab_molarity, tab_dilution = st.tabs(["Mass & Molarity (Mass ↔ M)", "Dilution Calculator (C₁V₁ = C₂V₂)"])

    # ---------------------------------------------------------
    # TAB 1: MASS & MOLARITY
    # ---------------------------------------------------------
    with tab_molarity:
        st.subheader("1. Substance Selection & Parsing")
        
        col_preset, col_custom = st.columns([1, 1])
        
        with col_preset:
            preset_choice = st.selectbox("Preset Reagent", list(PRESET_REAGENTS.keys()))
        
        with col_custom:
            if preset_choice == "Custom (Your formula)":
                formula_input = st.text_input("Chemical Formula (e.g. CuSO4*5H2O, NaCl, C6H12O6)", value="NaCl")
            else:
                # Извлекаем формулу из названия (до скобки)
                formula_input = preset_choice.split(" ")[0]
                st.text_input("Selected Formula", value=formula_input, disabled=True)

        # Parsing ChemPy
        substance, mw, parse_error = parse_formula_with_chempy(formula_input)

        if parse_error:
            st.error(parse_error)
            st.stop()

        # Отображение информации о веществе из ChemPy
        st.success(f"**Parsed Formula:** `{substance.unicode_name}` | **Calculated MW:** `{mw:.4f} g/mol`")

        st.divider()
        st.subheader("2. Calculation Parameters")

        col_purity, col_target = st.columns([1, 2])
        with col_purity:
            purity = st.number_input("Purity / Assay (%)", min_value=0.1, max_value=100.0, value=100.0, step=0.5)
        with col_target:
            target = st.radio(
                "Calculate:",
                ["Mass required (m)", "Volume needed (V)", "Molarity (C)"],
                horizontal=True
            )

        col1, col2, col3 = st.columns(3)

        # Inputs
        with col1:
            if target == "Mass required (m)":
                st.text_input("Mass (m)", value="Calculating...", disabled=True)
                mass_val = 0.0
                mass_unit = "g"
            else:
                mass_val = st.number_input("Mass", value=1.0, min_value=1e-7, format="%.4f")
                mass_unit = st.selectbox("Mass Unit", ["g", "mg", "µg"], key="m_unit")

        with col2:
            if target == "Molarity (C)":
                st.text_input("Concentration (C)", value="Calculating...", disabled=True)
                conc_val = 0.0
                conc_unit = "mM"
            else:
                conc_val = st.number_input("Concentration", value=1.0, min_value=1e-9, format="%.4f")
                conc_unit = st.selectbox("Conc. Unit", ["M", "mM", "µM", "nM"], key="c_unit")

        with col3:
            if target == "Volume needed (V)":
                st.text_input("Volume (V)", value="Calculating...", disabled=True)
                vol_val = 0.0
                vol_unit = "mL"
            else:
                vol_val = st.number_input("Volume", value=100.0, min_value=1e-7, format="%.4f")
                vol_unit = st.selectbox("Vol. Unit", ["L", "mL", "µL"], key="v_unit")

        # Приведение к единицам СИ (г, моль/л, л)
        purity_factor = purity / 100.0

        if target != "Mass required (m)":
            m_g = mass_val * {"g": 1.0, "mg": 1e-3, "µg": 1e-6}[mass_unit]
        if target != "Molarity (C)":
            c_m = conc_val * {"M": 1.0, "mM": 1e-3, "µM": 1e-6, "nM": 1e-9}[conc_unit]
        if target != "Volume needed (V)":
            v_l = vol_val * {"L": 1.0, "mL": 1e-3, "µL": 1e-6}[vol_unit]

        st.divider()
        st.subheader("3. Results & Preparation Protocol")

        if target == "Mass required (m)":
            # m = C * V * MW / purity
            mass_required_g = (c_m * v_l * mw) / purity_factor
            
            if mass_required_g >= 1.0:
                res_str = f"{mass_required_g:.4f} g"
            elif mass_required_g >= 1e-3:
                res_str = f"{mass_required_g * 1e3:.3f} mg"
            else:
                res_str = f"{mass_required_g * 1e6:.2f} µg"

            st.metric(label="Required Mass", value=res_str)
            
            # Дополнительная мета-информация (w/v %)
            wv_percent = (mass_required_g / (v_l * 1000)) * 100

            st.info(
                f"**Recipe for Electronic Lab Notebook (ELN):**\n\n"
                f"1. Weigh **{res_str}** of `{formula_input}` (Purity: {purity}%, MW: {mw:.2f} g/mol).\n"
                f"2. Dissolve in diluent (ddH₂O/buffer) to a final volume of **{vol_val} {vol_unit}**.\n"
                f"3. Final Concentration: **{conc_val} {conc_unit}** (approx. **{wv_percent:.3f}% w/v**)."
            )

        elif target == "Volume needed (V)":
            vol_l = (m_g * purity_factor) / (c_m * mw)
            
            if vol_l >= 1.0:
                res_str = f"{vol_l:.4f} L"
            elif vol_l >= 1e-3:
                res_str = f"{vol_l * 1e3:.3f} mL"
            else:
                res_str = f"{vol_l * 1e6:.2f} µL"

            st.metric(label="Resulting Volume", value=res_str)

        elif target == "Molarity (C)":
            c_calc_m = (m_g * purity_factor) / (mw * v_l)
            
            if c_calc_m >= 1.0:
                res_str = f"{c_calc_m:.4f} M"
            elif c_calc_m >= 1e-3:
                res_str = f"{c_calc_m * 1e3:.3f} mM"
            elif c_calc_m >= 1e-6:
                res_str = f"{c_calc_m * 1e6:.2f} µM"
            else:
                res_str = f"{c_calc_m * 1e9:.2f} nM"

            st.metric(label="Calculated Molarity", value=res_str)

    # ---------------------------------------------------------
    # TAB 2: DILUTION CALCULATOR
    # ---------------------------------------------------------
    with tab_dilution:
        st.subheader("Dilution Calculator (C₁V₁ = C₂V₂)")
        
        col_c1, col_v1 = st.columns(2)
        with col_c1:
            c1 = st.number_input("Stock Concentration (C₁)", value=10.0, min_value=1e-9)
            c1_unit = st.selectbox("C₁ Unit", ["X", "M", "mM", "µM", "%"], key="c1_u")
        with col_v1:
            st.text_input("Stock Volume Needed (V₁)", value="Calculated below", disabled=True)

        col_c2, col_v2 = st.columns(2)
        with col_c2:
            c2 = st.number_input("Desired Concentration (C₂)", value=1.0, min_value=1e-9)
            c2_unit = st.selectbox("C₂ Unit", ["X", "M", "mM", "µM", "%"], key="c2_u")
        with col_v2:
            v2 = st.number_input("Desired Final Volume (V₂)", value=100.0, min_value=1e-9)
            v2_unit = st.selectbox("V₂ Unit", ["mL", "L", "µL"], key="v2_u")

        if c1_unit == c2_unit:
            if c1 > 0 and c2 <= c1:
                v1 = (c2 * v2) / c1
                buffer_v = v2 - v1
                
                st.divider()
                st.metric(label="Volume of Stock (V₁) needed", value=f"{v1:.3f} {v2_unit}")
                
                if buffer_v >= 0:
                    st.success(
                        f"**Dilution Instructions:**\n\n"
                        f"Add **{v1:.3f} {v2_unit}** of Stock (C₁ = {c1} {c1_unit}) to "
                        f"**{buffer_v:.3f} {v2_unit}** of solvent/buffer to yield **{v2} {v2_unit}** of {c2} {c2_unit} solution."
                    )
            else:
                st.warning("Stock concentration (C₁) must be higher than target concentration (C₂).")
        else:
            st.info("💡 Ensure C₁ and C₂ use matching concentration units for direct C₁V₁=C₂V₂ calculations.")

if __name__ == "__main__":
    st.set_page_config(page_title="Molarity Calculator", layout="wide")
    render_molarity_calculator()
