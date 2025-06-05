import time
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Real-Time HVAC Control Simulator",
    page_icon="🌡️",
    layout="wide",
)

st.title("Real-Time HVAC Control Simulator")
st.caption("Live Monitoring, Prediction, and Energy Analytics")

# Initialize state
if "temp_data" not in st.session_state:
    st.session_state.temp_data = pd.DataFrame(columns=["time", "actual_temp", "pred_temp"])
    st.session_state.energy_data = pd.DataFrame(columns=["time", "energy"])
    st.session_state.counter = 0

# Main simulation loop (1 iteration per rerun)
now = datetime.now()
val = st.session_state.counter * 10
st.session_state.temp_data = pd.concat(
    [st.session_state.temp_data,
     pd.DataFrame([{
         "time": now,
         "actual_temp": val,
         "pred_temp": val + np.random.normal(0, 2),
     }])],
    ignore_index=True
)
st.session_state.energy_data = pd.concat(
    [st.session_state.energy_data,
     pd.DataFrame([{
         "time": now,
         "energy": val
     }])],
    ignore_index=True
)
st.session_state.counter += 1

# Layout
room_col, energy_col = st.columns(2)

# Line chart for temperature
with room_col:
    st.subheader("Room Temperature")
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(
        x=st.session_state.temp_data["time"],
        y=st.session_state.temp_data["actual_temp"],
        name="Actual Temp",
        line=dict(color="black", width=2)
    ))
    fig_temp.add_trace(go.Scatter(
        x=st.session_state.temp_data["time"],
        y=st.session_state.temp_data["pred_temp"],
        name="Predicted Temp",
        line=dict(dash="dash", color="gray", width=2)
    ))
    # Comfort band shading (21-23 °C)
    fig_temp.add_shape(
        type="rect",
        xref="paper", yref="y",
        x0=0, x1=1, y0=21, y1=23,
        fillcolor="lightgreen", opacity=0.3, layer="below", line_width=0,
    )
    fig_temp.update_layout(
        yaxis_title="°C",
        xaxis_title="",
        showlegend=True,
        height=400
    )
    st.plotly_chart(fig_temp, use_container_width=True)

# Line chart for energy
with energy_col:
    st.subheader("Energy Consumption")
    fig_energy = go.Figure()
    fig_energy.add_trace(go.Scatter(
        x=st.session_state.energy_data["time"],
        y=st.session_state.energy_data["energy"],
        name="Energy Used",
        line=dict(color="blue", width=2)
    ))
    fig_energy.update_layout(
        yaxis_title="kWh",
        xaxis_title="Time",
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_energy, use_container_width=True)

# Delay and rerun
time.sleep(5)
st.rerun()
