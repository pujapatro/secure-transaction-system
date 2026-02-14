import requests
import random
import time

API_URL = "http://127.0.0.1:8000/orders"

def generate_order(order_num):
    """
    Enforces EXACT uniform distribution:
    25% 3W
    25% 3W EV
    25% 4W
    25% 4W EV
    """

    bucket = order_num % 4

    if bucket == 0:
        weight = random.randint(1, 80)        # 3W
    elif bucket == 1:
        weight = random.randint(1, 80)        # 3W EV
    elif bucket == 2:
        weight = random.randint(120, 160)     # 4W
    else:
        weight = random.randint(120, 160)     # 4W EV

    return {
        "order_id": f"ORD_{order_num}",
        "latitude": random.uniform(19.0, 19.3),
        "longitude": random.uniform(72.8, 73.0),
        "weight": weight,
        "priority": random.choice(["LOW", "MEDIUM", "HIGH"])
    }

order_num = 1

while True:
    order = generate_order(order_num)
    response = requests.post(API_URL, json=order)

    print(
        f"{order['order_id']} | "
        f"Weight: {order['weight']} | "
        f"Status: {response.status_code}"
    )

    order_num += 1
    time.sleep(3)
