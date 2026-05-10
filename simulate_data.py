import requests
import time
import random
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Endpoint for submitting sensor data
URL = "http://127.0.0.1:8000/api/data/"
MAX_RETRIES = 3
RETRY_DELAY = 10


def send_sensor_data():
    """Send simulated sensor data to API"""
    retry_count = 0

    logger.info("Starting sensor data simulation...")
    logger.info(f"Target URL: {URL}")

    while True:
        try:
            # Generate fake sensor data
            data = {
                "power": random.randint(100, 800),      # Watts
                "voltage": random.randint(220, 240),    # Volts
                "current": round(random.uniform(0.5, 5.0), 2)  # Amps
            }

            # Send POST request
            response = requests.post(URL, json=data, timeout=5)
            response.raise_for_status()  # Raise error for bad status codes

            logger.info(f"Sent: {data}")
            logger.info(f"Response: {response.json()}")
            retry_count = 0  # Reset retry counter on success

        except requests.exceptions.Timeout:
            retry_count += 1
            logger.error(f"Request timeout (Retry {retry_count}/{MAX_RETRIES})")
        except requests.exceptions.ConnectionError:
            retry_count += 1
            logger.error(f"Connection error - server might be down (Retry {retry_count}/{MAX_RETRIES})")
        except requests.exceptions.RequestException as e:
            retry_count += 1
            logger.error(f"Request error: {e} (Retry {retry_count}/{MAX_RETRIES})")
        except Exception as e:
            retry_count += 1
            logger.error(f"Unexpected error: {e} (Retry {retry_count}/{MAX_RETRIES})")

        # Check retry limit
        if retry_count >= MAX_RETRIES:
            logger.warning("Max retries reached, resetting counter")
            retry_count = 0

        # Wait before next attempt
        time.sleep(5)


if __name__ == "__main__":
    try:
        send_sensor_data()
    except KeyboardInterrupt:
        logger.info("Simulator stopped by user")
        sys.exit(0)