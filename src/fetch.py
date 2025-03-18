import uvicorn
from fastapi import FastAPI
import logging
import time
import psutil
from sqlalchemy import create_engine, text

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Correct MySQL Database URL (Replace with your credentials)
DATABASE_URL = "mysql+pymysql://root:pass@localhost/dummy_db"

engine = create_engine(DATABASE_URL)

def fetch_system_metrics():
    """Fetch CPU, memory, and disk usage from MySQL database."""
    try:
        start_time = time.time()  # ✅ Start response time tracking
        
        # ✅ Connect to MySQL
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM report ORDER BY collection_time DESC LIMIT 1;"))
            data = result.fetchone()

        # ✅ Get system metrics
        system_stats = {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "db_metrics": dict(data._mapping) if data else None,  # ✅ Proper conversion
            "response_time": round(time.time() - start_time, 4)
        }

        return system_stats

    except Exception as e:
        logger.error(f"❌ Error fetching system metrics: {e}")
        return {"error": str(e)}


def get_top_processes(n=5):
    """Fetch top N processes sorted by CPU usage."""
    processes = []
    for proc in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    # ✅ Sort by CPU usage (descending) and return top N
    return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:n]

@app.get("/fetch")
def fetch_monitor_time():
    """API endpoint to fetch system metrics and top running processes."""
    return fetch_system_metrics()

if __name__ == "__main__":
    logger.info("🚀 Monitor service is running!")
    uvicorn.run(app, host="0.0.0.0", port=8503)
