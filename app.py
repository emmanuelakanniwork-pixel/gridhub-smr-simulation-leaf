import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="GRIDHUB SMR Simulation", layout="wide")

st.title("GRIDHUB: SMR Energy Network Simulation")
st.markdown("Interactive Grid Stability & Electrification Model")

st.sidebar.header("System Parameters")

base_demand_avg = st.sidebar.slider("Base Average Demand (MW)", 400, 800, 500)
peak_variation = st.sidebar.slider("Daily Demand Variation (MW)", 100, 300, 200)
ev_peak_load = st.sidebar.slider("EV Evening Charging Peak (MW)", 0, 300, 120)
renewable_capacity = st.sidebar.slider("Installed Renewable Capacity (MW)", 100, 600, 300)
smr_capacity = st.sidebar.slider("SMR Baseload Capacity (MW)", 0, 600, 300)
demand_growth_percent = st.sidebar.slider("Future Demand Growth (%)", 0, 50, 20)

hours = np.arange(0, 24)

base_demand = base_demand_avg + peak_variation * np.sin((hours - 7) / 24 * 2 * np.pi)

ev_load = np.zeros(24)
ev_load[18:22] = ev_peak_load

total_demand = (base_demand + ev_load) * (1 + demand_growth_percent / 100)

np.random.seed(1)
renewables = renewable_capacity * (
    0.6 + 0.3 * np.sin(hours / 24 * 2 * np.pi)
) + np.random.normal(0, renewable_capacity * 0.05, 24)

renewables = np.clip(renewables, 0, None)

smr_output = np.full(24, smr_capacity)

total_supply = renewables + smr_output

shortfall = total_demand - total_supply
backup_required = np.where(shortfall > 0, shortfall, 0)

col1, col2, col3 = st.columns(3)

col1.metric("Peak Demand (MW)", int(np.max(total_demand)))
col2.metric("Peak Backup Required (MW)", int(np.max(backup_required)))
col3.metric("Total Daily Backup Energy (MWh)", int(np.sum(backup_required)))

fig1, ax1 = plt.subplots()
ax1.plot(hours, total_demand, label="Demand")
ax1.plot(hours, total_supply, label="Supply (Renewables + SMR)")
ax1.set_xlabel("Hour of Day")
ax1.set_ylabel("Power (MW)")
ax1.set_title("Grid Balance Over 24 Hours")
ax1.legend()

st.pyplot(fig1)

fig2, ax2 = plt.subplots()
ax2.bar(hours, backup_required)
ax2.set_xlabel("Hour of Day")
ax2.set_ylabel("Backup Required (MW)")
ax2.set_title("Fossil Backup Required")

st.pyplot(fig2)