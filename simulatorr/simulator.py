import time
import requests
import random

while True:
    try:
        status = requests.get("http://127.0.0.1:8000/api/device/status/").json()

        if status["on"]:
            voltage = random.uniform(210, 240)
            current = random.uniform(0.5, 5)
        else:
            voltage = 0
            current = 0

        power = voltage * current

        data = {
            "voltage": voltage,
            "current": current,
            "power": power,
            "device_on": status["on"]
        }

        requests.post("http://127.0.0.1:8000/api/data/", json=data)

        print("Sent:", data)

    except:
        print("Server error")

    time.sleep(5)