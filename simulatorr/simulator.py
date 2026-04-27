import time
import requests
import random
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_URL = "http://127.0.0.1:8000"
STATUS_ENDPOINT = f"{BASE_URL}/api/device/status/"
# ✅ CORRECTED: Changed from /api/data/ to /api/data/post/
DATA_ENDPOINT = f"{BASE_URL}/api/data/post/"


def get_device_status():
    """Fetch current device status from API"""
    try:
        response = requests.get(STATUS_ENDPOINT, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get device status: {e}")
        return None


def send_sensor_data(status_data):
    """Send sensor data to API based on device status"""
    try:
        if status_data["on"]:
            voltage = round(random.uniform(210, 240), 2)
            current = round(random.uniform(0.5, 5), 2)
        else:
            voltage = 0
            current = 0

        power = round(voltage * current, 2)

        data = {
            "voltage": voltage,
            "current": current,
            "power": power,
            "device_on": status_data["on"]
        }

        response = requests.post(DATA_ENDPOINT, json=data, timeout=5)
        response.raise_for_status()

        logger.info(f"Sent: {data}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send sensor data: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


def main():
    """Main simulator loop"""
    logger.info("Starting device simulator...")
    logger.info(f"Status Endpoint: {STATUS_ENDPOINT}")
    logger.info(f"Data Endpoint: {DATA_ENDPOINT}")

    while True:
        try:
            status_data = get_device_status()
            if status_data:
                send_sensor_data(status_data)
            else:
                logger.warning("Could not get device status, skipping data send")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")

        time.sleep(5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Simulator stopped by user")
        sys.exit(0)