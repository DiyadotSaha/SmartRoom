import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import time

st.set_page_config(page_title="Real-Time HVAC Control Simulator", layout="wide")

st.markdown("<meta http-equiv='refresh' content='5'>", unsafe_allow_html=True)
st.caption(f"Refreshed at {pd.Timestamp.now().strftime('%H:%M:%S')}")

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

# --- Load CSV and extract room1 data ---
@st.cache_data(ttl=5)
def load_room1_data():
    df = pd.read_csv("output_csv_smart.csv")
    df["time"] = pd.to_datetime(df["time"])
    df = df.tail(30)  # Limit to latest 30 rows
    df["room_name"] = "Room 1"
    return df[["room_name", "time", "room_temp", "energy", "command"]]

room_df = load_room1_data()

# --- Layout ---
st.markdown("### Room Temperature")
left_col, right_col = st.columns(2)

# --- Temperature Overview ---
with left_col:
    st.selectbox("", ["Room 1"], index=0)

    fig, ax = plt.subplots(figsize=(6, 2.7))
    ax.plot(room_df["time"], room_df["room_temp"], label="Room Temp", color="black", linewidth=2)
    ax.axhspan(21, 23, color='green', alpha=0.1)
    ax.set_ylim([19, 28])
    ax.set_ylabel("°C")
    ax.legend(loc="upper right")
    ax.grid(True)
    st.pyplot(fig)

    current_temp = room_df["room_temp"].iloc[-1]
    current_command = room_df["command"].iloc[-1]

    stat_col1, stat_col2, stat_col3 = st.columns(3)
    stat_col1.metric("Current Temperature", f"{current_temp:.1f}°C")
    in_range = "In Range" if 21 <= current_temp <= 23 else "Out of Range"
    stat_col2.markdown(f"<b>Comfort Status</b><br><span style='color:green;'>{in_range}</span>", unsafe_allow_html=True)
    stat_col3.markdown(f"<b>HVAC State</b><br>{current_command.capitalize()}", unsafe_allow_html=True)

# --- Energy Overview ---
with right_col:
    st.markdown("### Energy Consumption")
    fig2, ax2 = plt.subplots(figsize=(6, 2.7))
    ax2.plot(room_df["time"], room_df["energy"].cumsum(), color='blue', linewidth=2)
    ax2.set_ylabel("kWh")
    ax2.grid(True)
    st.pyplot(fig2)

    e_col1, e_col2 = st.columns(2)
    total_energy = room_df["energy"].sum()
    e_col1.metric("Total Energy Used", f"{total_energy:.2f} kWh")
    avg_power = (room_df["energy"].mean() * 60)  # kWh per hour approximation
    e_col2.metric("Average Power", f"{avg_power:.2f} kW")

    
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = time.time()
    else:
        now = time.time()
        if now - st.session_state.last_refresh >= 5:
            st.session_state.last_refresh = now
            st.experimental_set_query_params(r=time.time())  # force rerun by query param change

