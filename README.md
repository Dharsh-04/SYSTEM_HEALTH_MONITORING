# 📊 System Health Monitoring

## 📌 Project Overview
This is a **real-time system health monitoring tool** built with **Streamlit**, which tracks and visualizes **API response times, system processes, and database restart events**. The system auto-refreshes at intervals and correlates database downtime with response time spikes.

## 🚀 Features
✅ **Live monitoring of system metrics** – Tracks CPU, memory, and running processes
✅ **Response time tracking** – Monitors API response time and detects slowdowns
✅ **Database restart simulation** – Randomly kills and restarts the database
✅ **Correlation Analysis** – Computes and visualizes Pearson correlation between response time and database restarts
✅ **Auto-refresh mechanism** – Updates every few seconds for real-time monitoring

## 🛠️ Setup & Installation
### 1️⃣ **Clone the repository**
```sh
 git clone https://github.com/your-repo/system-health-monitoring.git
 cd system-health-monitoring
```

### 2️⃣ **Install dependencies**
Make sure you have Python installed, then run:
```sh
pip install -r requirements.txt
```

### 3️⃣ **Run the Streamlit App**
```sh
streamlit run src/app.py
```

## 📊 Expected Output
- **Real-time graphs** showing API response time, system process usage, and restart events
- **Correlation insights** between API slowdowns and database restarts
- **Automatic restart triggers** every 5 minutes with response-time monitoring

## 📌 Future Improvements
- **Expand monitoring** to include disk I/O and network usage
- **Alerts & notifications** when system metrics exceed thresholds
- **Integration with Grafana or Prometheus** for advanced monitoring



