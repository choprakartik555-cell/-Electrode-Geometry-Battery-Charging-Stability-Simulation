import streamlit as st
import pybamm
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. UI CONFIGURATION & SPACE THEME ---
st.set_page_config(page_title="Electrode Geometry & Battery Simulation", layout="wide")

# Enhanced CSS for an animated "Deep Space" background
st.markdown("""
    <style>
    /* Main background with a radial cosmic glow */
    .stApp {
        background: radial-gradient(circle at center, #1b2735 0%, #090a0f 100%);
        background-attachment: fixed;
    }

    /* Moving "Star" particles effect using a repeating linear gradient */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: 
            radial-gradient(white, rgba(255,255,255,.2) 2px, transparent 40px),
            radial-gradient(white, rgba(255,255,255,.15) 1px, transparent 30px),
            radial-gradient(white, rgba(255,255,255,.1) 2px, transparent 20px);
        background-size: 550px 550px, 350px 350px, 250px 250px;
        background-position: 0 0, 40px 60px, 130px 270px;
        opacity: 0.3;
        z-index: -1;
    }

    /* Move the title upward */
    .main .block-container {
        padding-top: 1.5rem;
    }

    /* Futuristic Card Styling for Metrics */
    [data-testid="stMetricValue"] { 
        font-size: 2rem; 
        color: #00d4ff; 
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    }
    
    .stMetric {
        background: rgba(0, 212, 255, 0.05); 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid rgba(0, 212, 255, 0.2);
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    
    /* Sidebar styling to match the space theme */
    [data-testid="stSidebar"] {
        background-color: rgba(9, 10, 15, 0.95);
        border-right: 1px solid rgba(0, 212, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR: PARAMETERS ---
with st.sidebar:
    st.header("🚀 System Parameters")
    chem_map = {"Chen2020 (NMC/Graphite)": "Chen2020", "OKane2022 (LCO/Graphite)": "OKane2022", "Ai2020 (LFP/Graphite)": "Ai2020"}
    selected_display = st.selectbox("Battery Chemistry", list(chem_map.keys()))
    battery_type = chem_map[selected_display]
    
    st.divider()
    st.subheader("⚡ Operational")
    charge_current = st.slider("Charge Current (A)", 0.1, 15.0, 7.5)
    temp_c = st.slider("Ambient Temp (°C)", -5, 55, 25)
    
    st.divider()
    st.subheader("❄️ Thermal Management")
    cooling_coeff = st.slider("Cooling Coefficient (W/m²K)", 0, 50, 10)
    st.caption("Lower value = higher heat buildup.")

    st.divider()
    st.subheader("🔬 Electrode Design")
    # Restored all geometry parameters
    n_thick = st.slider("Anode Thickness (μm)", 50, 200, 100) / 1e6
    p_thick = st.slider("Cathode Thickness (μm)", 50, 200, 100) / 1e6
    p_rad = st.slider("Neg. Particle Radius (μm)", 1, 15, 5) / 1e6
    active_frac = st.slider("Active Material Fraction", 0.5, 0.95, 0.75)

# --- 3. PHYSICS KERNEL ---
@st.cache_data
def run_simulation(choice, current, temp, n_t, p_t, p_r, a_f, cooling):
    options = {"thermal": "lumped"}
    if choice == "OKane2022":
        options.update({"SEI": "ec reaction limited", "lithium plating": "partially reversible"})
        
    model = pybamm.lithium_ion.DFN(options)
    params = pybamm.ParameterValues(choice)

    # Physics-based updates including restored geometry
    params.update({
        "Upper voltage cut-off [V]": 5.0, 
        "Ambient temperature [K]": temp + 273.15,
        "Current function [A]": -abs(current),
        "Negative electrode thickness [m]": n_t,
        "Positive electrode thickness [m]": p_t,
        "Negative particle radius [m]": p_r,
        "Negative electrode active material volume fraction": a_f,
        "Total heat transfer coefficient [W.m-2.K-1]": cooling,
        "Contact resistance [Ohm.m2]": 0.02 
    }, check_already_exists=False)

    sim = pybamm.Simulation(model, parameter_values=params)
    try:
        sol = sim.solve([0, 900]) # 15 min window
        return sol
    except Exception as e:
        return "SOLVER CRASH: Physical limits exceeded (Mass transport or Stoichiometric saturation)."

sol = run_simulation(battery_type, charge_current, temp_c, n_thick, p_thick, p_rad, active_frac, cooling_coeff)

# --- 4. DASHBOARD DISPLAY ---
if isinstance(sol, str):
    st.error(f"⚠️ Physics Divergence: {sol}")
else:
    st.title("🔋 Electrode Geometry & Battery Charging Stability Simulation")
    
    v_final = sol['Terminal voltage [V]'].entries[-1]
    t_max_c = sol['X-averaged cell temperature [K]'].entries.max() - 273.15
    anode_var = "Negative electrode surface potential difference at separator interface [V]"
    anode_pot = sol[anode_var].entries[-1]

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Terminal Voltage", f"{v_final:.2f} V")
    m2.metric("Max Cell Temp", f"{t_max_c:.1f} °C")
    m3.metric("Anode Potential", f"{anode_pot:.4f} V")
    m4.metric("Ambient Temp", f"{temp_c} °C")
    m5.metric("Cooling Coeff.", f"{cooling_coeff} W/m²K")

    # The 8-Graph Grid
    st.subheader("Internal Electrochemical State Analysis")
    fig = make_subplots(rows=2, cols=4, horizontal_spacing=0.1, vertical_spacing=0.2,
                        subplot_titles=("Voltage Profile", "Thermal Response", "Electrolyte Conc.", "Interfacial Current",
                                       "Anode Potential", "Cathode Potential", "Anode Surf. Conc.", "Cathode Surf. Conc."))

    t_min = sol["Time [min]"].entries
    plot_map = [
        ("Terminal voltage [V]", "Voltage [V]", 1, 1),
        ("X-averaged cell temperature [K]", "Temp [K]", 1, 2),
        ("X-averaged electrolyte concentration [mol.m-3]", "Conc [mol/m³]", 1, 3),
        ("X-averaged negative electrode interfacial current density [A.m-2]", "Current [A/m²]", 1, 4),
        (anode_var, "Potential [V]", 2, 1), 
        ("X-averaged positive electrode potential [V]", "Potential [V]", 2, 2),
        ("X-averaged negative particle surface concentration [mol.m-3]", "Conc [mol/m³]", 2, 3),
        ("X-averaged positive particle surface concentration [mol.m-3]", "Conc [mol/m³]", 2, 4)
    ]

    for var, y_label, r, c in plot_map:
        fig.add_trace(go.Scatter(x=t_min, y=sol[var].entries, mode='lines', line=dict(color='#00d4ff', width=2)), row=r, col=c)
        fig.update_xaxes(title_text="Time [min]", row=r, col=c)
        fig.update_yaxes(title_text=y_label, row=r, col=c, tickformat=".3f")

    fig.update_layout(height=750, template="plotly_dark", showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    # --- 5. BMS SAFETY ASSESSMENT ---
    st.divider()
    st.subheader("🛡️ BMS Safety Assessment")
    reasons = []
    if t_max_c > 50: reasons.append(f"Thermal Violation: {t_max_c:.1f}°C (Limit: 50°C).")
    if temp_c < 0: reasons.append("Sub-zero hazard: High risk of lithium plating.")
    if anode_pot < 0.005: reasons.append(f"Plating Risk: Anode Potential at {anode_pot*1000:.1f} mV.")
    if v_final > 5.0: reasons.append(f"Overvoltage: {v_final:.2f}V (Limit: 5.0V).")

    if not reasons:
        st.success(f"✅ **SAFE TO CHARGE:** Parameters are within safe operation boundaries.")
    else:
        st.error("❌ **CHARGING UNSAFE:** The BMS detected safety violations:")
        for r in reasons: st.write(f"- {r}")
