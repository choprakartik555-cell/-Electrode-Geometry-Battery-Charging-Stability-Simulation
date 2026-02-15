# -Electrode-Geometry-Battery-Charging-Stability-Simulation

This project is a high-fidelity **Digital Twin** designed to simulate and analyze the internal electrochemical behavior of lithium-ion batteries under various charging conditions and physical designs. Built for battery engineers and researchers, the application leverages the **Doyle-Fuller-Newman (DFN)** model to provide real-time insights into state-of-the-art safety boundaries.

### 🔬 Core Methodology

The simulation utilizes **PyBaMM** (Python Battery Mathematical Modelling) to solve the complex partial differential equations governing ion transport and electrochemical kinetics within the cell. Unlike simple equivalent circuit models, this physics-based approach allows for the monitoring of internal variables—such as **Anode Surface Potential**—which are critical for predicting degradation and lithium plating during fast charging.

### 🛰️ Key Features

* **Multi-Chemistry Support:** Analyze and compare performance across three major chemistries: **NMC** (Nickel Manganese Cobalt), **LFP** (Lithium Iron Phosphate), and **LCO** (Lithium Cobalt Oxide).
* **Parametric Design Deck:** Interactively adjust electrode geometry, including anode/cathode thickness, particle radius, and active material fractions, to observe their impact on rate capability.
* **Dynamic Thermal Management:** Features a lumped thermal model where users can manipulate the **Cooling Coefficient** () and ambient temperature to simulate various Thermal Management System (TMS) efficiencies.
* **BMS Safety Engine:** An integrated **Battery Management System (BMS)** diagnostic tool that monitors for:
* **Lithium Plating Risk:** Threshold detection when anode potential drops below .
* **Thermal Runaway Boundaries:** Real-time violation alerts if internal temperatures exceed .
* **Overcharge Detection:** Safety interlocks for terminal voltages exceeding .



### 🛠️ Technical Stack

* **Physics Engine:** PyBaMM (Doyle-Fuller-Newman Model)
* **Frontend:** Streamlit (Futuristic "Deep Space" UI)
* **Data Visualization:** Plotly (High-precision 8-graph telemetry grid)
* **Language:** Python 3.10+

### 🚀 Usage Instructions

1. **Configure Parameters:** Use the sidebar to set your target chemistry and charging current.
2. **Optimize Geometry:** Adjust electrode thickness to see the trade-off between energy density and charging stability.
3. **Monitor Telemetry:** Observe the **8-graph grid** to track electrolyte concentration gradients, interfacial current densities, and thermal response.
4. **Evaluate Safety:** Check the **BMS Safety Assessment** at the bottom of the dashboard to ensure the selected configuration is safe for operation.

---

**Developed by Kartik Chopra**

*Master of Science in Chemical Engineering, Purdue University


**Would you like me to add a "Project Background" section that explains the specific electrochemical equations used in the DFN model?**
