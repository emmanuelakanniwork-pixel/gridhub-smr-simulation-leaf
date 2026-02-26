import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

st.set_page_config(page_title="SMR Energy Policy Simulator", layout="wide")

st.title("⚡ SMR Energy Transition Simulation Platform")
st.markdown("A dynamic modelling tool evaluating EV growth, grid demand, SMR deployment, cost efficiency and carbon impact.")

# -----------------------------
# Sidebar Inputs
# -----------------------------
st.sidebar.header("Model Inputs")

years = st.sidebar.slider("Simulation Years", 5, 30, 20)
base_demand = st.sidebar.number_input("Current Grid Demand (TWh)", 100, 1000, 300)
ev_growth = st.sidebar.slider("Annual EV Growth Rate (%)", 1, 30, 10)

num_smrs = st.sidebar.slider("Number of SMRs Installed", 1, 20, 5)
smr_output = st.sidebar.number_input("Output per SMR (TWh/year)", 10, 200, 50)

cost_smr = st.sidebar.number_input("SMR Cost (£/MWh)", 40, 200, 90)
cost_gas = st.sidebar.number_input("Gas Cost (£/MWh)", 40, 200, 120)

carbon_smr = st.sidebar.number_input("SMR Carbon (gCO2/kWh)", 0, 50, 12)
carbon_gas = st.sidebar.number_input("Gas Carbon (gCO2/kWh)", 300, 600, 450)

sensitivity = st.sidebar.checkbox("Apply +20% Demand Shock")

# -----------------------------
# Model Calculations
# -----------------------------
years_array = np.arange(years)

base_projection = base_demand * (1 + ev_growth/100) ** years_array
shock_projection = base_projection * 1.2

if sensitivity:
    demand = shock_projection
else:
    demand = base_projection

total_smr_supply = num_smrs * smr_output
smr_supply = np.full(years, total_smr_supply)

supply_gap = smr_supply - demand

# Cost modelling
annual_cost_smr = demand * 1_000_000 * cost_smr / 1_000_000
annual_cost_gas = demand * 1_000_000 * cost_gas / 1_000_000

# Carbon modelling
carbon_smr_total = demand * carbon_smr
carbon_gas_total = demand * carbon_gas

# -----------------------------
# Dashboard Layout
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Demand vs SMR Supply")
    fig1, ax1 = plt.subplots()
    ax1.plot(years_array, base_projection)
    ax1.plot(years_array, shock_projection)
    ax1.plot(years_array, smr_supply)
    ax1.legend(["Base Demand", "Demand +20%", "SMR Supply"])
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Energy (TWh)")
    st.pyplot(fig1)

with col2:
    st.subheader("🌍 Carbon Emissions Comparison")
    fig2, ax2 = plt.subplots()
    ax2.plot(years_array, carbon_smr_total)
    ax2.plot(years_array, carbon_gas_total)
    ax2.legend(["SMR Emissions", "Gas Emissions"])
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Carbon (Relative Index)")
    st.pyplot(fig2)

st.subheader("💷 Annual System Cost Comparison")
fig3, ax3 = plt.subplots()
ax3.plot(years_array, annual_cost_smr)
ax3.plot(years_array, annual_cost_gas)
ax3.legend(["SMR Cost", "Gas Cost"])
ax3.set_xlabel("Year")
ax3.set_ylabel("Cost (£ Millions Approx.)")
st.pyplot(fig3)

# -----------------------------
# Policy Summary
# -----------------------------
st.subheader("📜 Policy Insight Summary")

if supply_gap[-1] >= 0:
    supply_message = "SMR deployment is sufficient to meet projected EV demand."
else:
    supply_message = "SMR deployment is insufficient under this scenario."

carbon_savings = carbon_gas_total[-1] - carbon_smr_total[-1]

st.write(f"""
• {supply_message}  
• Estimated long-term carbon savings vs gas: {int(carbon_savings):,} (relative index units)  
• SMRs provide cost stability compared to volatile gas pricing.  
• Increased EV adoption significantly increases grid stress without firm low-carbon baseload.
""")

# -----------------------------
# PDF Export
# -----------------------------
def generate_pdf():
    doc = SimpleDocTemplate("SMR_Report.pdf")
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("SMR Energy Transition Simulation Report", styles["Title"]))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(supply_message, styles["Normal"]))
    elements.append(Paragraph(f"Carbon savings vs gas: {int(carbon_savings)}", styles["Normal"]))

    doc.build(elements)

generate_pdf()

with open("SMR_Report.pdf", "rb") as file:
    st.download_button("📥 Download Policy Report (PDF)", file, "SMR_Report.pdf")
