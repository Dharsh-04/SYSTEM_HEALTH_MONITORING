import pymysql
import pandas as pd
import streamlit as st
import time
import plotly.express as px
import requests
import subprocess
import psutil  
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from threading import Thread
from streamlit_autorefresh import st_autorefresh
from streamlit.runtime.scriptrunner import add_script_run_ctx
import matplotlib.pyplot as plt
import seaborn as sns
# ✅ MySQL Connection (Dockerized)
DB_CONFIG = {
    "host": "mysql_container",
    "user": "root",
    "password": "pass",
    "database": "dummy_db",
}
engine = create_engine(f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}")

# ✅ Initialize session states
session_defaults = {
    "response_times": [],
    "killing_spikes": [],
    "process_metrics": [],
    "last_kill_time": datetime.now() - timedelta(minutes=10),
    "last_fetch_time": datetime.now() - timedelta(minutes=1),
    "app_start_time": datetime.now(),
    "timestamps": [],
}
for key, value in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ✅ Streamlit UI
st.title("📊 System Health Monitoring")
st.subheader("📈 Process Metrics, API Response & Database Restarts")

graph_metrics = st.empty()
graph_response = st.empty()
graph_killing = st.empty()
graph_correlation = st.empty()  # ✅ Add this line


# ✅ Fetch API response time
def fetch_response_time():
    now = datetime.now()
    st.session_state.timestamps.append(now.strftime("%H:%M:%S"))
    start_time = time.time()
    
    try:
        response = requests.get("http://127.0.0.1:8503/fetch", timeout=5)
        response_time = round(time.time() - start_time, 4)
    except requests.RequestException:
        response_time = 5.0

    st.session_state.response_times.append(response_time)
    st.session_state.response_times = st.session_state.response_times[-50:]
    st.session_state.timestamps = st.session_state.timestamps[-50:]

# ✅ Fetch running process metrics
def fetch_process_metrics():
    process_data = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            process_data.append({
                "Timestamp": time.strftime("%H:%M:%S"),
                "Process ID": proc.info['pid'],
                "Process Name": proc.info['name'],
                "CPU_Usage": proc.info['cpu_percent'],
                "Memory_Usage": proc.info['memory_percent']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return process_data

# ✅ Trigger killing script at correct intervals
def trigger_killing_script():
    now = datetime.now()
    elapsed_since_start = now - st.session_state.app_start_time
    elapsed_since_last_kill = now - st.session_state.last_kill_time

    if elapsed_since_start >= timedelta(seconds=20) and elapsed_since_last_kill >= timedelta(minutes=1):
        subprocess.Popen(["python", "killing.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        st.session_state.killing_spikes.append(1)
        st.session_state.killing_spikes = st.session_state.killing_spikes[-50:]
        st.session_state.last_kill_time = now
        print(f"🔴 Database Restart Triggered at {now.strftime('%H:%M:%S')}")

        # ✅ Start background thread to reset spike after 20s
        reset_spike_thread = Thread(target=reset_spike)
        reset_spike_thread.start()
    
    # ✅ Maintain the same length for timestamps and killing_spikes
    while len(st.session_state.killing_spikes) < len(st.session_state.timestamps):
        st.session_state.killing_spikes.insert(0, 0)  # Append 0 for missing timestamps

# ✅ Reset the spike back to 0 after 20 seconds
def reset_spike():
    time.sleep(20)  # Wait for 20s after the spike
    if "killing_spikes" in st.session_state and st.session_state.killing_spikes:
        st.session_state.killing_spikes.append(0)  # Append 0 instead of modifying last element
        st.session_state.timestamps.append(datetime.now().strftime("%H:%M:%S"))  # Maintain sync
reset_spike_thread = Thread(target=reset_spike)
add_script_run_ctx(reset_spike_thread)  # This ensures Streamlit can track the thread
reset_spike_thread.start()

# ✅ Continuous data fetching
fetch_response_time()
st.session_state.process_metrics = fetch_process_metrics()
trigger_killing_script()

# ✅ Convert session state to DataFrames
df_process = pd.DataFrame(st.session_state.process_metrics)
min_length = min(len(st.session_state.timestamps), len(st.session_state.response_times), len(st.session_state.killing_spikes))

st.session_state.timestamps = st.session_state.timestamps[-min_length:]
st.session_state.response_times = st.session_state.response_times[-min_length:]
st.session_state.killing_spikes = st.session_state.killing_spikes[-min_length:]

df_response = pd.DataFrame({"Timestamp": st.session_state.timestamps, "Response_Time": st.session_state.response_times})
df_killing = pd.DataFrame({"Timestamp": st.session_state.timestamps, "Spike": st.session_state.killing_spikes})


# ✅ Compute Pearson Correlation if data is sufficient
if len(st.session_state.response_times) > 1 and len(st.session_state.killing_spikes) > 1:
    correlation = pd.Series(st.session_state.response_times).corr(pd.Series(st.session_state.killing_spikes), method='pearson')
    st.write(f"📉 Pearson Correlation between Response Time and Restart Events: {correlation:.4f}")
    
    # ✅ Create DataFrame for heatmap
    df_correlation = pd.DataFrame({"Response_Time": st.session_state.response_times, "Restart_Spike": st.session_state.killing_spikes})
    correlation_matrix = df_correlation.corr(method='pearson')

    # ✅ Heatmap Plot
    plt.figure(figsize=(6, 4))
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", cbar=True)
    plt.title("Correlation Matrix between Response Time and Database Restart Events")
    st.pyplot(plt)
else:
    st.write("📉 Pearson Correlation: Not enough data yet.")
# ✅ Ensure process data exists before plotting
if not df_process.empty:
    top_processes = df_process.sort_values(by=["CPU_Usage", "Memory_Usage"], ascending=False).head(10)
    fig_metrics = px.bar(top_processes, x="Process Name", y=["CPU_Usage", "Memory_Usage"],
                          title="Top 10 Processes by CPU & Memory Usage",
                          labels={"value": "Usage (%)", "Process Name": "Running Process"},
                          barmode="group")
    graph_metrics.plotly_chart(fig_metrics, use_container_width=True)
else:
    graph_metrics.write("🔄 Waiting for process metrics data...")

if df_response.empty:
    graph_response.write("🔄 Waiting for response time data...")
else:
    fig_response = px.line(df_response, x="Timestamp", y="Response_Time",
                          title="API Response Time Over Time",
                          labels={"Response_Time": "Time (s)", "Timestamp": "Time"},
                          line_shape="spline", markers=True)
    graph_response.plotly_chart(fig_response, use_container_width=True)

fig_killing = px.line(df_killing, x="Timestamp", y="Spike",
                      title="Database Restart Events",
                      labels={"Spike": "Restart Triggered", "Timestamp": "Time"},
                      line_shape="spline", markers=True)
graph_killing.plotly_chart(fig_killing, use_container_width=True)


# ✅ Auto-refresh page every 7 seconds
st_autorefresh(interval=7000, key="refresh")