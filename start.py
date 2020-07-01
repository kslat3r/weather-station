#!/usr/bin/python

import os
from sense_hat import SenseHat
from influxdb import InfluxDBClient
import datetime
import time

def get_cpu_temp():
    res = os.popen("vcgencmd measure_temp").readline()
    return float(res.replace("temp=","").replace("'C\n", ""))

def get_temperature(sense):
    sense_temp = sense.get_temperature()
    cpu_temp = get_cpu_temp()
    return sense_temp - ((cpu_temp - sense_temp) / 1.5)

try:
    sense = SenseHat()
    sense.set_rotation(180)

    client = InfluxDBClient("localhost", 8086, "root", "root", "logger_db")

    while True:
        timestamp = datetime.datetime.utcnow().isoformat()

        temperature = get_temperature(sense)
        humidity = sense.get_humidity()
        pressure = sense.get_pressure()

        datapoints = [{
            "measurement": "test1",
            "tags": {},
            "time": timestamp,
            "fields": {
                "temperaturevalue": temperature,
                "humidityvalue": humidity,
                "pressurevalue": pressure
            }
        }]

        client.write_points(datapoints)

        sense.show_message(str(round(temperature)) + "c " + str(round(humidity)) + "%RH " + str(round(pressure)) + "mBar", text_colour=[100, 100, 100])

        time.sleep(5)
except KeyboardInterrupt:
	print("Exit")
