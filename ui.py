import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

# ——————————————————————————————————————————————————————————————————————
# 1) STREAMLIT PAGE SETUP
# ——————————————————————————————————————————————————————————————————————

# Page config MUST come first
st.set_page_config(page_title="Real-Time HVAC Control Simulator", layout="wide")

# Auto‐refresh every 5 seconds via HTML meta tag
st.markdown("<meta http-equiv='refresh' content='5'>", unsafe_allow_html=True)
st.caption(f"Refreshed at {pd.Timestamp.now().strftime('%H:%M:%S')}")

# Matplotlib style settings
mpl.rcParams['font.size']       = 10
mpl.rcParams['axes.titlesize']  = 11
mpl.rcParams['axes.labelsize']  = 10
mpl.rcParams['legend.fontsize'] = 8

# ——————————————————————————————————————————————————————————————————————
# 2) LOAD CSV (LATEST 30 ROWS)
# ——————————————————————————————————————————————————————————————————————

def load_latest_data():
    """
    Reads 'output_csv_smart.csv', converts 'time' to datetime,
    and returns the most recent 30 rows of data.
    CSV columns expected: time, room_temp, energy, command
    """
    df = pd.read_csv("/Users/asad/SmartRoom/room1_output_logs/output_csv_smart.csv")
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").tail(30)
    return df

room_df = load_latest_data()

# ——————————————————————————————————————————————————————————————————————
# 3) HEADER + CONTROLS
# ——————————————————————————————————————————————————————————————————————

header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.markdown("""
        <h1 style='margin-bottom: 0;'>Real-Time HVAC Control Simulator</h1>
        <p style='font-size: 20px; margin-top: 0;'>Live Monitoring, Prediction, and Energy Analytics</p>
    """, unsafe_allow_html=True)

with header_col2:
    st.markdown("<div style='text-align: right;'>Predictive Control</div>", unsafe_allow_html=True)
    st.toggle("", value=True)  # Just a visual toggle; no backend logic here
    st.markdown("<div style='text-align: right;'>Demo Mode</div>", unsafe_allow_html=True)
    st.radio("", ["Reactive", "Predictive"], horizontal=True)

# ——————————————————————————————————————————————————————————————————————
# 4) LAYOUT: TEMPERATURE GRAPH + ENERGY GRAPH SIDE-BY-SIDE
# ——————————————————————————————————————————————————————————————————————

st.markdown("### Room Temperature")
left_col, right_col = st.columns(2)

# --- Left column: Room Temperature Overview ---
with left_col:
    st.selectbox("", ["Room 1"], index=0)  # Hard‐coded to “Room 1”

    # Plot: room_temp over time
    fig, ax = plt.subplots(figsize=(6, 2.7))
    ax.plot(room_df["time"], room_df["room_temp"],
            label="Room Temp", color="black", linewidth=2)
    # Shade comfort band (21°C–23°C):
    ax.axhspan(21, 23, color="green", alpha=0.1)
    ax.set_ylim([19, 28])
    ax.set_ylabel("°C")
    ax.legend(loc="upper right")
    ax.grid(True)
    st.pyplot(fig)

    # Latest values for metrics
    current_temp     = room_df["room_temp"].iloc[-1]
    current_command  = room_df["command"].iloc[-1]

    stat_col1, stat_col2, stat_col3 = st.columns(3)
    stat_col1.metric("Current Temperature", f"{current_temp:.1f}°C")

    # Comfort status (in or out of 21–23°C)
    if 21 <= current_temp <= 23:
        stat_col2.markdown(
            "<b>Comfort Status</b><br><span style='color:green;'>In Range</span>",
            unsafe_allow_html=True
        )
    else:
        stat_col2.markdown(
            "<b>Comfort Status</b><br><span style='color:orange;'>Out of Range</span>",
            unsafe_allow_html=True
        )

    # HVAC state icon + label
    hstate = current_command.strip().lower()
    if hstate != "off" and hstate != "":
        stat_col3.markdown(
            f"<b>HVAC State</b><br> {hstate.capitalize()}",
            unsafe_allow_html=True
        )
    else:
        stat_col3.markdown(
            "<b>HVAC State</b><br>Off",
            unsafe_allow_html=True
        )

# --- Right column: Energy Consumption Overview ---
with right_col:
    st.markdown("### Energy Consumption")
    fig2, ax2 = plt.subplots(figsize=(6, 2.7))
    ax2.plot(room_df["time"], room_df["energy"].cumsum(),
             color="blue", linewidth=2)
    ax2.set_ylabel("kWh")
    ax2.grid(True)
    st.pyplot(fig2)

    total_energy = room_df["energy"].sum()
    avg_power    = room_df["energy"].mean() * 60  # approximate kW (assuming 1-min intervals)

    e_col1, e_col2 = st.columns(2)
    e_col1.metric("Total Energy Used", f"{total_energy:.2f} kWh")
    e_col2.metric("Average Power",     f"{avg_power:.2f} kW")
