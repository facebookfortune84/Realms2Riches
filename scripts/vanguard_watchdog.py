import time
import requests
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("VANGUARD_WATCHDOG")

BACKEND_URL = "https://api.realms2riches.com"
CHECK_INTERVAL = 300  # 5 minutes

def check_health():
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10, headers={"": "true"})
        if response.status_code == 200:
            logger.info("✅ System Pulse: SOVEREIGN. All systems operational.")
            return True
        else:
            logger.warning(f"⚠️ System Pulse: WEAK ({response.status_code}).")
            return False
    except Exception as e:
        logger.error(f"❌ System Pulse: FLATLINE. Error: {e}")
        return False

def restart_stack():
    logger.info("🔄 Initiating Emergency Recovery Sequence...")
    try:
        # Restart Docker Compose
        subprocess.run(["docker-compose", "-f", "infra/docker/docker-compose.prod.yml", "restart"], check=True)
        logger.info("✅ Docker Stack Restarted.")
        
        # Ngrok is usually handled by the host process, but we assume it's running.
        # If ngrok is down, the start script needs to be re-run.
    except Exception as e:
        logger.error(f"❌ Recovery Failed: {e}")

def run_watchdog():
    logger.info("🛡️ VANGUARD WATCHDOG ACTIVE. Monitoring the Matrix...")
    while True:
        if not check_health():
            restart_stack()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run_watchdog()

