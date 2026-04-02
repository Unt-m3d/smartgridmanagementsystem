import requests
import time
import random

# Your Django API endpoint
URL = "http://127.0.0.1:8000/api/data/"

while True:
    try:
        # Generate fake sensor data
        data = {
            "power": random.randint(100, 800),      # Watts
            "voltage": random.randint(220, 240),    # Volts
            "current": round(random.uniform(0.5, 5.0), 2)  # Amps
        }

        # Send POST request
        response = requests.post(URL, json=data)

        print("Sent:", data)
        print("Response:", response.json())

    except Exception as e:
        print("Error:", e)

    # Wait 5 seconds
    time.sleep(5)