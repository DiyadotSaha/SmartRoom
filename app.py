import streamlit as st
import pandas as pd
import random

# Simulated real-time data sources
def simulate_sensor_data():
    return {
        'temperature': random.randint(68, 80),
        'humidity': random.randint(30, 60)
    }

def simulate_user_feedback():
    users = ['User A', 'User B', 'User C']
    statuses = ['too hot', 'comfortable', 'too cold']
    return [{'user': u, 'status': random.choice(statuses)} for u in users]

def simulate_hvac_command():
    return random.choice(['increase AC', 'decrease AC', 'do nothing'])

def simulate_user_preferences():
    return {
        'User A': '72°F',
        'User B': '75°F',
        'User C': '70°F'
    }

st.set_page_config(page_title="SmartRoom Notifier", layout="wide")
st.title(" SmartRoom Notifier Dashboard")

col1, col2 = st.columns(2)

with col1:
    st.subheader(" Real-Time Sensor Data")
    sensor_data = simulate_sensor_data()
    st.metric("Temperature", f"{sensor_data['temperature']} °F")
    st.metric("Humidity", f"{sensor_data['humidity']} %")

with col2:
    st.subheader(" User Feedback")
    feedback = simulate_user_feedback()
    for f in feedback:
        st.text(f"{f['user']} says: {f['status']}")

st.subheader(" HVAC Control Decision")
hvac_command = simulate_hvac_command()
st.success(f"System Command: {hvac_command}")

st.subheader(" Occupant Preferences")
prefs = simulate_user_preferences()
for user, pref in prefs.items():
    st.text(f"{user}: prefers {pref}")

st.subheader(" Comfort Trends (Mock Data)")
sample_data = pd.DataFrame({
    'Time': pd.date_range(end=pd.Timestamp.now(), periods=10),
    'Temperature': [random.randint(68, 80) for _ in range(10)],
    'Feedback Score': [random.randint(-1, 1) for _ in range(10)]
})
st.line_chart(sample_data.set_index('Time'))

st.subheader(" Send Manual Feedback")
col3, col4 = st.columns(2)
with col3:
    if st.button("I'm too hot"):
        st.write(" Feedback sent: too hot")
with col4:
    if st.button("I'm too cold"):
        st.write(" Feedback sent: too cold")
