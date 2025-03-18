import docker
import time

DB_CONTAINER_NAME = "mysql_container"  # Name of your MySQL container
client = docker.from_env()  # Connect to Docker

def restart_database():
    """Simulate DB failure by stopping and restarting the MySQL container."""
    try:
        container = client.containers.get(DB_CONTAINER_NAME)
        if container.status == "running":
            print(f"⚠️ Stopping database container {DB_CONTAINER_NAME} for 20 seconds...")
            container.stop()
            time.sleep(20)  # Keep DB down for 20 seconds

            print(f"✅ Restarting database container {DB_CONTAINER_NAME}...")
            container.start()
            print("✅ Database restarted successfully.")
        else:
            print(f"⚠️ Database container {DB_CONTAINER_NAME} is not running, skipping restart.")

    except Exception as e:
        print(f"❌ Error handling database restart: {e}")

if __name__ == "__main__":
    print("⏳ Waiting 20 seconds before the first DB restart...")
    #time.sleep(20)  # ✅ First kill after 20s

    while True:
        restart_database()  # ✅ Kill DB
        print("⏳ Waiting 1 minute before the next restart...")
        #time.sleep(60)  # ✅ Repeat every 1 minute
