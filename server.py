from flask import Flask, render_template
from flask import request
from flask_socketio import SocketIO, emit
from flask_apscheduler import APScheduler
from datetime import datetime
import math
import mysql.connector

app = Flask(__name__)
socketio = SocketIO(app)

db = mysql.connector.connect(
  host="localhost",
  user="admin",
  password="admin",
  database="rideshare"
)

riders = []
drivers = []

scheduler = APScheduler()

@scheduler.task('interval', id='match_driver_rider', seconds=3, misfire_grace_time=None)
def match_driver_rider():
    def selection_logic(data):
        now = datetime.now()
        duration = now-data['time']
        if duration.total_seconds() > 5:
            return True
        return False

    riders_waited = list(filter(selection_logic, riders))
    drivers_waited = list(filter(selection_logic, drivers))
    # print(riders_waited)

    def calculate_distance(driver, rider):
        rx, ry = [int(x) for x in rider['coords']]
        dx, dy = [int(x) for x in driver['coords']]
        
        return math.sqrt((rx-dx)**2+(ry-dy)**2)
    
    for r in riders_waited:
        nearest_distance = 999999999
        closest_driver = None
        for d in drivers_waited:
            distance = calculate_distance(d, r)
            if distance < nearest_distance:
                nearest_distance = distance
                closest_driver = d["name"]

        if closest_driver != None:
            riders[:] = list(filter(lambda x: x['name'] != r['name'], riders))
            drivers[:] = list(filter(lambda x: x['name'] != d['name'], drivers))
            data = {
                "driver":r["name"],
                "rider":d["name"]
            }
            socketio.emit('message', data, namespace='/communication')

@app.route('/rider', methods = ['POST'])
def rider():
    data = request.json
    data['time'] = datetime.now()
    riders.append(data)
    return {"status": "received rider request"}

@app.route('/driver', methods = ['POST'])
def driver():
    data = request.json
    data['time'] = datetime.now()
    drivers.append(data)
    return {"status": "received driver request"}

@app.route('/rating', methods = ['POST'])
def rating():
    return {"status": "ok"}

if __name__ == '__main__':
    scheduler.start()
    socketio.run(app, port=8000)