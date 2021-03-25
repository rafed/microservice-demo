import requests
import random
import time
import string
import names
import socketio

rider_api = "http://localhost:8000/rider"
driver_api = "http://localhost:8000/driver"

def rand_coords():
    v = random.randint(-100,100)
    return v

if __name__ == "__main__":
    sio = socketio.Client()
    sio.connect('http://localhost:8000', namespaces=['/communication'])

    @sio.on('message', namespace='/communication')
    def on_connect(data):
        print(f"[*] Driver {data['driver']} matched with {data['rider']}")

    while True:
        rider_data = {
            "name": names.get_full_name(),
            "coords": [rand_coords(), rand_coords()],
            "destination": [rand_coords(), rand_coords()]
        }

        driver_data = {
            "name": names.get_full_name(),
            "car_number": ''.join(random.choice(string.ascii_lowercase) for i in range(5)) ,
            "coords": [rand_coords(), rand_coords()]
        }

        r = requests.post(rider_api, json=rider_data)
        print(r.status_code, rider_data["name"], "searching for a car")

        r = requests.post(driver_api, json=driver_data)
        print(r.status_code, driver_data["name"], "searching for a passenger")

        print()
        time.sleep(1)
