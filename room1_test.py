import os
import sys
import time
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from HVACPublisher import publish_HVAC_command

topic_name = "room_1"
room_data = '/Users/asad/SmartRoom/room1.csv'
room_output = '/Users/asad/SmartRoom/room_output'

os.makedirs(room_output, exist_ok=True)
# Memory of past N steps
history_window = 12  # last 6 readings (30 seconds if step_interval is 5s)
room_temp_history = []

# Simulation parameters
comfort_range = (20.0, 22.0)
rolling_window_size = 5 * 60 * 1000  # 5 minutes in ms
step_interval = 5  # seconds
cooling_rate = 0.2
heating_rate = 0.1

energy_constants = {
    "fixed": {
        "cooling_power_kw": 5.0,
        "heating_power_kw": 4.5
    },
    "delta": {
        "K": 2.5
    },
    "cop": {
        "cop": 3.0,
        "fan_power_kw": 1.0,
        "cooling_capacity_kw": 10.0
    }
}




def apply_passive_drift(window, room_temp, drift_rate=0.1):
    if window.empty:
        return room_temp  # No change if no data
    ambient_temp = window['temperature'].rolling(window=3, min_periods=1).mean().iloc[-1]
    avg_humidity = window['relative_humidity'].mean()
    humidity_factor = 1 - (avg_humidity / 100) * 0.4
    humidity_factor = max(0.1, humidity_factor)
    temp_diff = ambient_temp - room_temp
    drift_strength = min(drift_rate * humidity_factor, abs(temp_diff))
    return room_temp + drift_strength if temp_diff > 0 else room_temp - drift_strength


def decision_cost(discomfort: float, energy: float, alpha: float = 1.0, beta: float = 10.0):
    return alpha * discomfort + beta * energy


def calculate_energy_usage(hvac_command, room_temp, setpoint, duration_sec=5, method="fixed", constants=None):
    if constants is None:
        constants = {}
    duration_hr = duration_sec / 3600
    if method == "fixed":
        if hvac_command == "cooling":
            return constants["cooling_power_kw"] * duration_hr
        elif hvac_command == "heating":
            return constants["heating_power_kw"] * duration_hr
        else:
            return 0.0
    elif method == "delta":
        diff = abs(room_temp - setpoint)
        return constants["K"] * diff * duration_hr if hvac_command != "off" else 0.0
    elif method == "cop":
        cop = constants.get("cop", 3.0)
        fan_power = constants.get("fan_power_kw", 1.0)
        cap = constants.get("cooling_capacity_kw", 10.0)
        load = max(room_temp - setpoint, 0) if hvac_command == "cooling" else max(setpoint - room_temp, 0)
        return ((load * cap / 5) / cop + fan_power) * duration_hr if hvac_command != "off" else 0.0
    raise ValueError("Unknown energy method")



def decide_command(room_temp, comfort_range):
    low, high = comfort_range
    if room_temp > high:
        return 'cooling', f"Room temp {room_temp:.2f} > upper bound {high}"
    elif room_temp < low:
        return 'heating', f"Room temp {room_temp:.2f} < lower bound {low}"
    return 'off', f"Room temp {room_temp:.2f} within comfort range"

def brute_force(df, duration_minutes, output_csv):
    print(f"🚀 Running brute force simulation for {duration_minutes} minutes...")
    start_time = df['time'].min()
    end_time = min(df['time'].max(), start_time + duration_minutes * 60 * 1000)
    current_time = start_time
    room_temp = df.iloc[0]['temperature']
    total_energy_kwh = 0.0
    output_rows = []
    while current_time <= end_time:
        window = df[(df['time'] >= current_time - rolling_window_size) & (df['time'] <= current_time)]
        if not window.empty:
            ambient_temp = window['temperature'].mean()
            humidity = window['relative_humidity'].mean()
            command, reason = decide_command(room_temp, comfort_range)
            energy_kwh = calculate_energy_usage(
                command,
                room_temp,
                sum(comfort_range) / 2,
                step_interval,
                "fixed",
                energy_constants["fixed"]  # ✅ only pass sub-dict
            )
            total_energy_kwh += energy_kwh

            if command == 'cooling':
                room_temp -= cooling_rate
            elif command == 'heating':
                room_temp += heating_rate
            else:
                room_temp = apply_passive_drift(window, room_temp)
            output_rows.append({
                "time": pd.to_datetime(current_time, unit='ms'),
                "command": command,
                "ambient_temp": round(ambient_temp, 2),
                "room_temp": round(room_temp, 2),
                "humidity": round(humidity, 2),
                "energy": round(energy_kwh, 4),
                "total_energy": round(total_energy_kwh, 2)
            })
        current_time += step_interval * 1000
        time.sleep(step_interval)
    pd.DataFrame(output_rows).to_csv(output_csv, index=False)
    print(f"✅ Brute force simulation complete. Output saved to {output_csv}")


def simulate_passive_temperature(df, duration_minutes, output_csv):
    print("")
    start_time = df['time'].min()
    end_time = min(df['time'].max(), start_time + duration_minutes * 60 * 1000)
    current_time = start_time
    room_temp = df.iloc[0]['temperature']
    output_rows = []

    while current_time <= end_time:
        window = df[(df['time'] >= current_time - rolling_window_size) & (df['time'] <= current_time)]
        if not window.empty:
            ambient_temp = window['temperature'].mean()
            avg_humidity = window['relative_humidity'].mean()

            room_temp = apply_passive_drift(window, room_temp)

            output_rows.append({
                "time": pd.to_datetime(current_time, unit='ms'),
                "command": "off",
                "ambient_temp": round(ambient_temp, 2),
                "room_temp": round(room_temp, 2),
                "humidity": round(avg_humidity, 2),
                "energy": 0.0,
                "total_energy": 0.0,
                "reason": "Passive simulation (no HVAC)"
            })

        current_time += step_interval * 1000
        time.sleep(step_interval)
    print(f"[{pd.to_datetime(current_time, unit='ms')}] Room: {room_temp:.2f}")

    pd.DataFrame(output_rows).to_csv(output_csv, index=False)
    print(f"✅ Passive simulation complete. Output saved to {output_csv}")


def linear_reg(df, duration_minutes, output_csv):
    print(f"Running smart simulation (linear regression + cost optimization) for {duration_minutes} minutes...")
    start_time = df['time'].min()
    end_time = min(df['time'].max(), start_time + duration_minutes * 60 * 1000)
    current_time = start_time
    room_temp = df.iloc[0]['temperature']
    total_energy_kwh = 0.0
    energy_method = "fixed"
    energy_cfg = energy_constants[energy_method]
    room_temp_history = []
    output_rows = []
    cooldown_period_ms = 60 * 1000
    last_command_time = start_time
    last_command = 'off'

    def decision_cost(discomfort: float, energy: float, alpha: float = 1.0, beta: float = 10.0):
        return alpha * discomfort + beta * energy

    while current_time <= end_time:
        window = df[(df['time'] >= current_time - rolling_window_size) & (df['time'] <= current_time)]
        if not window.empty:
            ambient_temp = window['temperature'].mean()
            avg_humidity = window['relative_humidity'].mean()

            room_temp_history.append(room_temp)
            if len(room_temp_history) > 50:
                room_temp_history.pop(0)

            smoothed_history = pd.Series(room_temp_history).rolling(window=3, min_periods=1).mean().tolist()
            if len(room_temp_history) >= history_window + 1:
                X = np.array([smoothed_history[i:i + history_window] for i in range(len(smoothed_history) - history_window)])
                y = np.array(smoothed_history[history_window:])
                model = LinearRegression().fit(X, y)
                last_window = np.array(room_temp_history[-history_window:]).reshape(1, -1)
                predicted_temp = model.predict(last_window)[0]
            else:
                predicted_temp = room_temp
            low, high = comfort_range

            # Decision optimization
            options = ['cooling', 'heating', 'off']
            best_command = 'off'
            min_cost = float('inf')
            for cmd in options:
                energy_kwh = calculate_energy_usage(
                    hvac_command=cmd,
                    room_temp=room_temp,
                    setpoint=(low + high) / 2,
                    duration_sec=step_interval,
                    method=energy_method,
                    constants=energy_cfg
                )
                # Simulate next room temperature
                temp_after = room_temp
                if cmd == 'cooling':
                    temp_after -= cooling_rate
                elif cmd == 'heating':
                    temp_after += heating_rate
                else:
                    temp_after = apply_passive_drift(window, room_temp)

                # Compute discomfort
                if temp_after > high:
                    discomfort = temp_after - high
                elif temp_after < low:
                    discomfort = low - temp_after
                else:
                    discomfort = 0.0

                cost = decision_cost(discomfort, energy_kwh, alpha=1.0, beta=10.0)
                if cost < min_cost:
                    min_cost = cost
                    best_command = cmd
                    best_energy = energy_kwh
                    best_discomfort = discomfort
                    temp_result = temp_after

            # Apply cooldown
            if (current_time - last_command_time) < cooldown_period_ms:
                command = last_command
                reason = f"Cooldown active: holding previous command {last_command}"
                best_energy = calculate_energy_usage(
                    hvac_command=command,
                    room_temp=room_temp,
                    setpoint=(low + high) / 2,
                    duration_sec=step_interval,
                    method=energy_method,
                    constants=energy_cfg
                )
                if command == 'cooling':
                    temp_result = room_temp - cooling_rate
                elif command == 'heating':
                    temp_result = room_temp + heating_rate
                else:
                    temp_result = apply_passive_drift(window, room_temp)
            else:
                command = best_command
                reason = f"Selected {best_command} with cost {min_cost:.4f} (Discomfort={best_discomfort:.2f}, Energy={best_energy:.4f})"
                last_command = command
                last_command_time = current_time
 
            room_temp = temp_result
            total_energy_kwh += best_energy

            publish_HVAC_command(command=command.encode('utf-8'), topic=topic_name)

            output_rows.append({
                "time": pd.to_datetime(current_time, unit='ms'),
                "command": command,
                "ambient_temp": round(ambient_temp, 2),
                "room_temp": round(room_temp, 2),
                "predicted_temp": round(predicted_temp, 2),
                "humidity": round(avg_humidity, 2),
                "energy": round(best_energy, 4),
                "total_energy": round(total_energy_kwh, 2),
                "reason": reason,
                "discomfort": round(best_discomfort, 2),
                "cost": round(min_cost, 4)
            })

        else:
            print(f"{pd.to_datetime(current_time, unit='ms')} | No ambient data in window")

        current_time += step_interval * 1000
        time.sleep(step_interval)
    pd.DataFrame(output_rows).to_csv(output_csv, index=False)
    print(f"✅ Smart simulation complete. Output saved to {output_csv}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python room1_test.py <duration_minutes> <mode>")
        print("Modes: brute, smart")
        return

    try:
        duration_minutes = int(sys.argv[1])
    except ValueError:
        print("Please provide an integer for the duration.")
        return

    mode = sys.argv[2].lower()
    output_csv = os.path.join(room_output, f"output_csv_{mode}.csv")

    # Load data
    df = pd.read_csv(room_data)
    df['time'] = pd.to_numeric(df['time'], errors='coerce')
    df = df.dropna(subset=['time']).sort_values(by='time').reset_index(drop=True)

    if mode == "brute":
        brute_force(df, duration_minutes, output_csv)
    elif mode == "smart":
        linear_reg(df, duration_minutes, output_csv)
    elif mode == "passive":
        simulate_passive_temperature(df, duration_minutes, output_csv)
    else:
        print("Unknown mode. Choose from: brute, smart.")

if __name__ == "__main__":
    main()