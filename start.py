#!/usr/bin/python

# -*- coding: utf-8 -*-

import os
from sense_hat import SenseHat
from influxdb import InfluxDBClient
import datetime
import time

def get_cpu_temp():
    res = os.popen("vcgencmd measure_temp").readline()
    return float(res.replace("temp=","").replace("'C\n",""))

def get_temperature(sense):
    sense_temp = sense.get_temperature()
    cpu_temp = get_cpu_temp()
    return sense_temp - ((cpu_temp - sense_temp) / 1.5)

try:
    sense = SenseHat()
    client = InfluxDBClient("localhost", 8086, "root", "root", "logger_db")

    while True:
        timestamp = datetime.datetime.utcnow().isoformat()

        temperature = get_temperature(sense)
        pressure = sense.get_pressure()
        humidity = sense.get_humidity()
        
        
        datapoints = [{
            "measurement": "test1",
            "tags": {},
            "time": timestamp,
            "fields": {
                "temperaturevalue": temperature,
                "pressurevalue": pressure,
                "humidityvalue": humidity
            }
        }]
        
        client.write_points(datapoints)

        sense.show_message("OK")
        
        time.sleep(5)
except KeyboardInterrupt:
    print("Exit")