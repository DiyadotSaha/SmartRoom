import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

st.set_page_config(page_title="Real-Time HVAC Control Simulator", layout="wide")

# -- Style config --
mpl.rcParams['font.size'] = 10
mpl.rcParams['axes.titlesize'] = 11
mpl.rcParams['axes.labelsize'] = 10
mpl.rcParams['legend.fontsize'] = 8

# --- Header ---
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.markdown("""
        <h1 style='margin-bottom: 0;'>Real-Time HVAC Control Simulator</h1>
        <p style='font-size: 20px; margin-top: 0;'>Live Monitoring, Prediction, and Energy Analytics</p>
    """, unsafe_allow_html=True)

with header_col2:
    st.markdown("<div style='text-align: right;'>Predictive Control</div>", unsafe_allow_html=True)
    st.toggle("", value=True)
    st.markdown("<div style='text-align: right;'>Demo Mode</div>", unsafe_allow_html=True)
    st.radio("", ["Reactive", "Predictive"], horizontal=True)

# --- Room Temperature and Energy Overview ---
st.markdown("### Room Temperature")
left_col, right_col = st.columns(2)

# --- Temperature Overview ---
with left_col:
    st.selectbox("", ["Room 1", "Room 2", "Room 3"], index=0)

    time = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='min')
    temp_actual = 22 + np.sin(np.linspace(0, 3 * np.pi, 30)) * 0.5 + np.random.normal(0, 0.2, 30)
    temp_predicted = temp_actual + np.random.normal(0, 0.3, 30)

    fig, ax = plt.subplots(figsize=(6, 2.7))
    ax.plot(time, temp_actual, label="Actual Temp", color="black", linewidth=2)
    ax.plot(time, temp_predicted, label="Predicted Temp", color="gray", linestyle="--", linewidth=2)
    ax.axhspan(21, 23, color='green', alpha=0.1)
    ax.set_ylim([19, 25])
    ax.set_ylabel("°C")
    ax.legend(loc="upper right")
    ax.grid(True)
    st.pyplot(fig)

    stat_col1, stat_col2, stat_col3 = st.columns(3)
    stat_col1.metric("Current Temperature", "22,3°C")
    stat_col2.markdown("<b>Comfort Status</b><br><span style='color:green;'>✅ In Range</span>", unsafe_allow_html=True)
    stat_col3.markdown("<b>HVAC State</b><br>🔵 Cooling", unsafe_allow_html=True)

# --- Energy Overview ---
with right_col:
    st.markdown("### Energy Consumption")
    energy_time = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='min')
    energy_data = np.cumsum(np.random.normal(0.1, 0.02, 30))

    fig2, ax2 = plt.subplots(figsize=(6, 2.7))
    ax2.plot(energy_time, energy_data, color='blue', linewidth=2)
    ax2.set_ylabel("kWh")
    ax2.grid(True)
    st.pyplot(fig2)

    e_col1, e_col2 = st.columns(2)
    e_col1.metric("Total Energy Used", "5,2 kWh")
    e_col2.metric("Average Power", "1,8 kW")
